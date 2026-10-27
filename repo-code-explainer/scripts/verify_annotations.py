#!/usr/bin/env python3
"""Conservative annotation checks. Never imports or executes inspected source.

Python 3.9+, standard library only. Full snapshots omit directory components
.git, __pycache__, .pytest_cache, .mypy_cache, .ruff_cache, .cache, node_modules,
and .venv. Symlinks in included paths fail closed, rather than being followed.
Explicit --paths may include normally omitted regular files. A snapshot proves
only its recorded scope, not that every file in an omitted directory is intact.
"""
import argparse
import ast
import difflib
import hashlib
import io
import json
import os
from pathlib import Path
import re
import sys
import tokenize

EXCLUDED = {'.git', '__pycache__', '.pytest_cache', '.mypy_cache', '.ruff_cache', '.cache', 'node_modules', '.venv'}
COOKIE = re.compile(br'coding[:=]\s*[-\w.]+')
DIRECTIVE = re.compile(r'\b(type\s*:|noqa\b|fmt\s*:|pylint\s*:|pyright\s*:|mypy\s*:|ruff\s*:|pragma\b|coding\s*[:=])', re.I)
LIMITATION = 'Structural checks do not prove behavioral equivalence for source inspection, line-number-sensitive behavior, external tools, or runtime environments.'


class Invalid(ValueError):
    pass


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def checked_file(path):
    path = Path(path).absolute()
    for entry in [path] + list(path.parents):
        if entry.is_symlink():
            raise Invalid('Symlink traversal rejected: ' + str(entry))
    if not path.is_file():
        raise Invalid('Not a regular file: ' + str(path))
    return path.resolve()


def source_file(root, relative):
    rel = Path(relative)
    if rel.is_absolute() or '..' in rel.parts or not rel.parts:
        raise Invalid('Expected contained relative file path: ' + str(relative))
    current = root
    for part in rel.parts:
        current = current / part
        if current.is_symlink():
            raise Invalid('Symlink traversal rejected: ' + str(relative))
    resolved = checked_file(current)
    if root not in resolved.parents:
        raise Invalid('Path escapes source root: ' + str(relative))
    return resolved


def inventory(root):
    paths = []
    for folder, dirs, files in os.walk(root, followlinks=False):
        # Do not follow links, even if they point back into the source tree.
        dirs[:] = sorted(d for d in dirs if d not in EXCLUDED)
        for name in dirs:
            if (Path(folder) / name).is_symlink():
                raise Invalid('Symlink directory rejected: ' + str(Path(folder) / name))
        for name in sorted(files):
            path = Path(folder) / name
            if path.is_symlink():
                raise Invalid('Symlink file rejected: ' + str(path))
            if not path.is_file():
                raise Invalid('Non-regular source entry rejected: ' + str(path))
            paths.append(path.relative_to(root).as_posix())
    return sorted(paths)


def containing_source(path):
    # For a standalone file the containing directory is the known source tree.
    for folder in [path.parent] + list(path.parent.parents):
        if (folder / '.git').exists():
            return folder
    return path.parent


def write_fresh(path, value, outside):
    dest = Path(path).absolute()
    # Existing parents must be real directories; do not resolve an output link.
    for ancestor in [dest] + list(dest.parents):
        if ancestor.is_symlink():
            raise Invalid('Symlink output path rejected: ' + str(ancestor))
    resolved = dest.resolve()
    outside = outside.resolve()
    if resolved == outside or outside in resolved.parents:
        raise Invalid('Evidence output must be outside source root')
    if not dest.parent.is_dir():
        raise Invalid('Evidence output parent must already exist')
    with dest.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')


def snapshot(source, output, paths=None):
    raw = Path(source).absolute()
    if any(entry.is_symlink() for entry in [raw] + list(raw.parents)) or not raw.is_dir():
        raise Invalid('Expected a real source directory without symlink traversal; use its canonical path')
    root = raw.resolve()
    selected = sorted(set(paths)) if paths else inventory(root)
    files = {rel: digest(source_file(root, rel)) for rel in selected}
    result = {'schema_version': 1, 'root': str(root), 'files': files,
              'full_inventory': not bool(paths), 'excluded_directories': sorted(EXCLUDED) if not paths else [],
              'status': 'pass', 'scope': 'Recorded regular files only; omitted directories are not verified.'}
    write_fresh(output, result, root)
    return result


def check_source(snapshot_path):
    data = json.loads(checked_file(snapshot_path).read_text(encoding='utf-8'))
    if (data.get('schema_version') != 1 or not isinstance(data.get('files'), dict)
            or not isinstance(data.get('root'), str)
            or not isinstance(data.get('full_inventory'), bool)
            or not all(isinstance(k, str) and isinstance(v, str) and re.fullmatch(r'[0-9a-f]{64}', v)
                       for k, v in data['files'].items())):
        raise Invalid('Unsupported or malformed snapshot schema')
    root = Path(data['root'])
    if root.is_symlink() or not root.is_dir():
        raise Invalid('Snapshot source root unavailable or linked')
    root = root.resolve()
    changed = []
    for rel, expected in data['files'].items():
        try:
            actual = digest(source_file(root, rel))
        except (Invalid, OSError):
            changed.append(rel)
            continue
        if actual != expected:
            changed.append(rel)
    added = []
    if data.get('full_inventory'):
        added = sorted(set(inventory(root)) - set(data['files']))
    return {'status': 'fail' if changed or added else 'pass', 'changed_or_missing': changed,
            'added': added, 'recorded_files': len(data['files']), 'scope': data.get('scope', 'Recorded files only')}


def encoding(data):
    return tokenize.detect_encoding(io.BytesIO(data).readline)[0]


def insertions(original, annotated):
    before = original.splitlines(keepends=True)
    after = annotated.splitlines(keepends=True)
    additions = []
    for tag, i, j, k, l in difflib.SequenceMatcher(None, before, after, autojunk=False).get_opcodes():
        if tag == 'equal':
            continue
        if tag != 'insert':
            raise Invalid('Original lines were changed, removed, or reordered')
        additions.extend((i, n, after[n]) for n in range(k, l))
    return before, after, additions


def python_tokens(data):
    ignored = {tokenize.COMMENT, tokenize.NL, tokenize.ENCODING, tokenize.ENDMARKER}
    return [(t.type, t.string) for t in tokenize.tokenize(io.BytesIO(data).readline) if t.type not in ignored]


def pair(original, annotated, language):
    left, right = checked_file(original), checked_file(annotated)
    if left == right:
        raise Invalid('Original and annotated paths must be separate files')
    a, b = left.read_bytes(), right.read_bytes()
    if language == 'none':
        return {'status': 'pass' if a == b else 'fail', 'language': 'none', 'byte_identical': a == b,
                'syntax': 'not_checked', 'equivalence': 'Byte identity only; format syntax not checked.', 'added_comment_lines': 0}
    before, after, added = insertions(a, b)
    codec = encoding(a) if language == 'python' else 'utf-8-sig'
    marker = '#' if language == 'python' else '%'
    for boundary, line_number, raw in added:
        line = raw.decode(codec).strip()
        if not line.startswith(marker):
            raise Invalid('Added line is not a complete native comment at output line ' + str(line_number + 1))
        if language == 'python':
            if line.startswith('#!') or DIRECTIVE.search(line):
                raise Invalid('Added directive is not an explanatory comment')
        else:
            if line.startswith(('%%', '%{', '%}', '%#', '%!')):
                raise Invalid('Added MATLAB section, block, or directive marker rejected')
            if boundary and b'...' in before[boundary - 1]:
                raise Invalid('Comment inserted into a possible MATLAB continuation')
    result = {'status': 'pass', 'language': language, 'added_comment_lines': len(added),
              'original_lines_preserved': True, 'limitation': LIMITATION}
    if language == 'python':
        if before and before[0].startswith(b'#!') and (not after or before[0] != after[0]):
            raise Invalid('Shebang moved from first line')
        for index, line in enumerate(before[:2]):
            if COOKIE.search(line) and (len(after) <= index or line != after[index]):
                raise Invalid('Encoding declaration moved')
        if encoding(a) != encoding(b):
            raise Invalid('Encoding changed')
        if python_tokens(a) != python_tokens(b):
            raise Invalid('Executable Python token sequence changed')
        tree_a = ast.parse(a, type_comments=True)
        tree_b = ast.parse(b, type_comments=True)
        # type_ignores retain source line numbers: compare their exact original
        # content through the insertion-only check, normalizing location here.
        for tree in (tree_a, tree_b):
            for node in ast.walk(tree):
                if isinstance(node, ast.TypeIgnore):
                    node.lineno = 0
        if ast.dump(tree_a, include_attributes=False) != ast.dump(tree_b, include_attributes=False):
            raise Invalid('Python syntax tree or type comments changed')
        compile(tree_a, str(left), 'exec')
        compile(tree_b, str(right), 'exec')
        result.update({'syntax': 'compiled_without_execution', 'executable_tokens_equal': True,
                       'normalized_ast_equal': True, 'equivalence': 'structural_only'})
    else:
        result.update({'syntax': 'unverified_no_matlab_parser', 'equivalence': 'unverified_manual_review_required',
                       'warning': 'Insertion-only and conservative continuation checks do not parse MATLAB strings, transpose, blocks, or directives. Run native validation where available.'})
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest='command', required=True)
    snap = sub.add_parser('snapshot', help='Hash selected/all regular files; write fresh evidence outside source')
    snap.add_argument('--source', required=True)
    snap.add_argument('--output', required=True)
    snap.add_argument('--paths', nargs='+')
    check = sub.add_parser('check-source', help='Check recorded hashes and full inventory if recorded')
    check.add_argument('--snapshot', required=True)
    compare = sub.add_parser('pair', help='Check insertion-only comments and optional Python structure')
    compare.add_argument('--original', required=True)
    compare.add_argument('--annotated', required=True)
    compare.add_argument('--language', required=True, choices=['python', 'matlab', 'none'])
    compare.add_argument('--report')
    args = parser.parse_args(argv)
    try:
        if args.command == 'snapshot':
            result = snapshot(args.source, args.output, args.paths)
        elif args.command == 'check-source':
            result = check_source(args.snapshot)
        else:
            result = pair(args.original, args.annotated, args.language)
            if args.report:
                write_fresh(args.report, result, containing_source(checked_file(args.original)))
        print(json.dumps(result, sort_keys=True))
        return 0 if result['status'] == 'pass' else 1
    except (Invalid, OSError, ValueError, SyntaxError, tokenize.TokenError, UnicodeError, KeyError, TypeError) as exc:
        print(json.dumps({'status': 'fail', 'error': str(exc)}))
        return 1


if __name__ == '__main__':
    sys.exit(main())
