import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import tokenize
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'verify_annotations.py'
spec = importlib.util.spec_from_file_location('verify_annotations', SCRIPT)
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


class VerifierTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name).resolve()
        self.source = self.root / 'source'
        self.output = self.root / 'output'
        self.source.mkdir()
        self.output.mkdir()

    def tearDown(self):
        self.temp.cleanup()

    def files(self, a, b, extension='py'):
        original = self.source / ('sample.' + extension)
        annotated = self.output / ('sample.' + extension)
        original.write_bytes(a)
        annotated.write_bytes(b)
        return original, annotated

    def py(self, a, b):
        return verify.pair(*self.files(a, b), 'python')

    def test_valid_python_structure_preserves_source(self):
        a = b'#!/usr/bin/env python3\n# coding: utf-8\n\ndef f(values):\n    """Existing docstring."""\n    return [x * 2 for x in values if x > 0]\n'
        b = a.replace(b'def f', b'# Transform only positive inputs.\ndef f').replace(b'    return', b'    # Double each retained value.\n    return')
        left, right = self.files(a, b)
        mode = left.stat().st_mode
        result = verify.pair(left, right, 'python')
        self.assertEqual(result['status'], 'pass')
        self.assertEqual(result['added_comment_lines'], 2)
        self.assertEqual(left.read_bytes(), a)
        self.assertEqual(left.stat().st_mode, mode)
        self.assertEqual(result['equivalence'], 'structural_only')

    def test_code_mutation_rejected(self):
        with self.assertRaises(verify.Invalid):
            self.py(b'x = 2\n', b'# Explain\nx = 3\n')

    def test_string_mutation_rejected(self):
        with self.assertRaises(verify.Invalid):
            self.py(b'x = "red"\n', b'# Explain\nx = "blue"\n')

    def test_comment_inside_multiline_string_rejected(self):
        with self.assertRaises(verify.Invalid):
            self.py(b'x = """one\ntwo"""\n', b'x = """one\n# Explanation\ntwo"""\n')

    def test_docstring_substitute_rejected(self):
        with self.assertRaises(verify.Invalid):
            self.py(b'def f():\n    return 1\n', b'def f():\n    """Explanation"""\n    return 1\n')

    def test_existing_comment_mutation_rejected(self):
        with self.assertRaises(verify.Invalid):
            self.py(b'# Existing\nx = 1\n', b'# New\nx = 1\n')

    def test_existing_directives_preserved(self):
        a = b'def f():\n    x = 1 # type: int\n    return x # type: ignore[return-value]\n'
        result = self.py(a, a.replace(b'    x', b'    # Create the local value.\n    x'))
        self.assertEqual(result['status'], 'pass')

    def test_added_directive_rejected(self):
        for comment in [b'# type: ignore\n', b'# noqa\n', b'# fmt: off\n', b'# coding: latin-1\n']:
            with self.subTest(comment=comment), self.assertRaises(verify.Invalid):
                self.py(b'x = 1\n', comment + b'x = 1\n')

    def test_shebang_move_rejected(self):
        with self.assertRaises(verify.Invalid):
            self.py(b'#!/usr/bin/python3\nx = 1\n', b'# Explanation\n#!/usr/bin/python3\nx = 1\n')

    def test_encoding_move_rejected(self):
        with self.assertRaises(verify.Invalid):
            self.py(b'# coding: utf-8\nx = 1\n', b'# Explanation\n# coding: utf-8\nx = 1\n')

    def test_invalid_python_rejected(self):
        with self.assertRaises((SyntaxError, tokenize.TokenError)):
            self.py(b'def f(:\n    pass\n', b'# Explain\ndef f(:\n    pass\n')

    def test_scope_invalid_code_rejected_by_compile(self):
        with self.assertRaises(SyntaxError):
            self.py(b'return 1\n', b'# Explain\nreturn 1\n')

    def test_python_backslash_continuation_rejected(self):
        with self.assertRaises((SyntaxError, verify.Invalid)):
            self.py(b'x = 1 + \\\n    2\n', b'x = 1 + \\\n# Explain\n    2\n')

    def test_added_blank_line_is_not_comment(self):
        with self.assertRaises(verify.Invalid):
            self.py(b'x = 1\n', b'\nx = 1\n')

    def test_utf8_bom_supported(self):
        a = b'\xef\xbb\xbfx = 1\n'
        b = b'\xef\xbb\xbfx = 1\n# A retained value.\n'
        self.assertEqual(self.py(a, b)['status'], 'pass')

    def test_matlab_valid_comments_report_limits(self):
        a = b'function y = scale(x)\ny = x(:, 1) * 2;\nend\n'
        b = a.replace(b'y = x', b'% Select and scale the first column.\ny = x')
        result = verify.pair(*self.files(a, b, 'm'), 'matlab')
        self.assertEqual(result['status'], 'pass')
        self.assertEqual(result['syntax'], 'unverified_no_matlab_parser')
        self.assertIn('unverified', result['equivalence'])

    def test_matlab_ellipsis_insertion_rejected(self):
        a = b'x = [1, ...\n2];\n'
        b = b'x = [1, ...\n% Explain\n2];\n'
        with self.assertRaises(verify.Invalid):
            verify.pair(*self.files(a, b, 'm'), 'matlab')

    def test_matlab_special_markers_rejected(self):
        for marker in [b'%% Section\n', b'%{\n', b'%}\n', b'%#ok\n']:
            with self.subTest(marker=marker), self.assertRaises(verify.Invalid):
                verify.pair(*self.files(b'x = 1;\n', marker + b'x = 1;\n', 'm'), 'matlab')

    def test_json_identity_and_changed_json(self):
        left, right = self.files(b'{"x": 0}\n', b'{"x": 0}\n', 'json')
        self.assertEqual(verify.pair(left, right, 'none')['status'], 'pass')
        right.write_bytes(b'// comment\n{"x": 0}\n')
        self.assertEqual(verify.pair(left, right, 'none')['status'], 'fail')

    def test_snapshot_full_and_stale_original(self):
        (self.source / 'one.py').write_bytes(b'x = 1\n')
        snap = self.output / 'before.json'
        verify.snapshot(self.source, snap)
        self.assertEqual(verify.check_source(snap)['status'], 'pass')
        (self.source / 'one.py').write_bytes(b'x = 2\n')
        self.assertEqual(verify.check_source(snap)['changed_or_missing'], ['one.py'])

    def test_snapshot_inventory_detects_add_and_delete(self):
        path = self.source / 'one.py'
        path.write_bytes(b'x = 1\n')
        snap = self.output / 'before.json'
        verify.snapshot(self.source, snap)
        path.unlink()
        (self.source / 'two.py').write_bytes(b'x = 1\n')
        result = verify.check_source(snap)
        self.assertEqual(result['status'], 'fail')
        self.assertEqual(result['added'], ['two.py'])
        self.assertEqual(result['changed_or_missing'], ['one.py'])

    def test_selected_snapshot_scope(self):
        (self.source / 'one.py').write_bytes(b'x = 1\n')
        (self.source / 'two.py').write_bytes(b'x = 2\n')
        snap = self.output / 'before.json'
        data = verify.snapshot(self.source, snap, ['one.py'])
        self.assertFalse(data['full_inventory'])
        (self.source / 'two.py').write_bytes(b'x = 3\n')
        self.assertEqual(verify.check_source(snap)['status'], 'pass')

    def test_snapshot_existing_output_rejected(self):
        snap = self.output / 'before.json'
        snap.write_text('preserve', encoding='utf-8')
        with self.assertRaises(FileExistsError):
            verify.snapshot(self.source, snap)
        self.assertEqual(snap.read_text(), 'preserve')

    def test_snapshot_inside_source_rejected(self):
        with self.assertRaises(verify.Invalid):
            verify.snapshot(self.source, self.source / 'before.json')
        self.assertFalse((self.source / 'before.json').exists())

    def test_traversal_and_absolute_paths_rejected(self):
        (self.root / 'outside.py').write_bytes(b'x = 0\n')
        for path in ['../outside.py', str(self.root / 'outside.py')]:
            with self.subTest(path=path), self.assertRaises(verify.Invalid):
                verify.snapshot(self.source, self.output / 'before.json', [path])

    def test_source_symlink_file_and_directory_rejected(self):
        outside = self.root / 'outside.py'
        outside.write_bytes(b'x = 1\n')
        (self.source / 'linked.py').symlink_to(outside)
        with self.assertRaises(verify.Invalid):
            verify.snapshot(self.source, self.output / 'before.json')
        (self.source / 'linked.py').unlink()
        (self.source / 'linked').symlink_to(self.output, target_is_directory=True)
        with self.assertRaises(verify.Invalid):
            verify.snapshot(self.source, self.output / 'before.json', ['linked/missing.py'])

    def test_pair_rejects_symlink_parent(self):
        left, right = self.files(b'x = 1\n', b'# Explain\nx = 1\n')
        link = self.root / 'linked-source'
        link.symlink_to(self.source, target_is_directory=True)
        with self.assertRaises(verify.Invalid):
            verify.pair(link / left.name, right, 'python')

    def test_snapshot_rejects_malformed_manifest(self):
        snap = self.output / 'bad.json'
        snap.write_text(json.dumps({'schema_version': 1, 'root': str(self.source), 'files': {'x': 'bad'}, 'full_inventory': True}))
        with self.assertRaises(verify.Invalid):
            verify.check_source(snap)

    def test_snapshot_excludes_only_declared_directories(self):
        (self.source / '.git').mkdir()
        (self.source / '.git' / 'ignored').write_bytes(b'git data')
        (self.source / 'src').mkdir()
        (self.source / 'src' / 'kept.py').write_bytes(b'x = 1\n')
        data = verify.snapshot(self.source, self.output / 'before.json')
        self.assertEqual(set(data['files']), {'src/kept.py'})
        self.assertEqual(data['excluded_directories'], sorted(verify.EXCLUDED))

    def test_report_cannot_overwrite_source(self):
        left, right = self.files(b'x = 1\n', b'# Explain\nx = 1\n')
        proc = subprocess.run([sys.executable, str(SCRIPT), 'pair', '--original', str(left), '--annotated', str(right), '--language', 'python', '--report', str(self.source / 'report.json')], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 1)
        self.assertFalse((self.source / 'report.json').exists())

    def test_cli_machine_readable_failure(self):
        left, right = self.files(b'x = 1\n', b'x = 2\n')
        proc = subprocess.run([sys.executable, str(SCRIPT), 'pair', '--original', str(left), '--annotated', str(right), '--language', 'python'], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 1)
        self.assertEqual(json.loads(proc.stdout)['status'], 'fail')


if __name__ == '__main__':
    unittest.main()
