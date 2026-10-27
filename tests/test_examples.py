"""Check actual public annotation examples without modifying source fixtures."""
import difflib
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / 'examples'
SOURCE = EXAMPLES / 'source'
DETAIL = EXAMPLES / 'candidate-detailed'
SECTION = EXAMPLES / 'candidate-sections'
SCRIPT = ROOT / 'repo-code-explainer/scripts/verify_annotations.py'
SPEC = importlib.util.spec_from_file_location('verify_examples', SCRIPT)
VERIFY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFY)


class PublishedExamples(unittest.TestCase):
    def test_python_preservation_and_path_coverage(self):
        for output, relative in [(SECTION, 'src/pipeline.py'), (DETAIL, 'src/pipeline.py'),
                                 (DETAIL, 'src/bridge.py')]:
            with self.subTest(output=output.name, relative=relative):
                result = VERIFY.pair(SOURCE / relative, output / relative, 'python')
                self.assertEqual(result['status'], 'pass')
                self.assertTrue(result['executable_tokens_equal'])
                self.assertTrue(result['normalized_ast_equal'])
        for relative in ['README.md', 'src/helpers.py']:
            self.assertEqual((SOURCE / relative).read_bytes(), (DETAIL / relative).read_bytes())

    def test_detail_levels_and_existing_comments(self):
        section = (SECTION / 'src/pipeline.py').read_text()
        detailed = (DETAIL / 'src/pipeline.py').read_text()
        self.assertGreater(sum(x.startswith('    #') for x in detailed.splitlines()),
                           sum(x.startswith('    #') for x in section.splitlines()))
        for text in [section, detailed]:
            self.assertEqual(text.count('# This message is data, including the literal # character.'), 1)
        self.assertIn('reverse', detailed.lower())
        self.assertIn('truthy', detailed.lower())

    def test_matlab_continuation_and_disclosed_limit(self):
        relative = 'matlab/scale_columns.m'
        result = VERIFY.pair(SOURCE / relative, DETAIL / relative, 'matlab')
        self.assertEqual(result['status'], 'pass')
        self.assertEqual(result['syntax'], 'unverified_no_matlab_parser')
        self.assertEqual(result['equivalence'], 'unverified_manual_review_required')
        self.assertIn('weights = [1, 2, ...\n           3, 4];', (DETAIL / relative).read_text())

    def test_strict_json_retains_zero_empty_and_companion(self):
        relative = 'config/settings.json'
        result = VERIFY.pair(SOURCE / relative, DETAIL / relative, 'none')
        self.assertTrue(result['byte_identical'])
        self.assertEqual(json.loads((DETAIL / relative).read_text()), {'workers': 0, 'paths': []})
        self.assertTrue((DETAIL / '.code-explainer/settings-explanation.md').is_file())

    @unittest.skipUnless(shutil.which('node'), 'Node unavailable')
    def test_javascript_insertion_and_native_parse(self):
        relative = 'web/transform.js'
        before = (SOURCE / relative).read_bytes().splitlines(keepends=True)
        after = (DETAIL / relative).read_bytes().splitlines(keepends=True)
        for tag, i, j, k, l in difflib.SequenceMatcher(None, before, after, autojunk=False).get_opcodes():
            self.assertIn(tag, ['equal', 'insert'])
            if tag == 'insert':
                self.assertTrue(all(line.lstrip().startswith(b'//') for line in after[k:l]))
        result = subprocess.run(['node', '--check', str(DETAIL / relative)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    @unittest.skipUnless(shutil.which('node'), 'Node unavailable')
    def test_python_to_node_runtime_in_isolated_copies(self):
        initial = {p.relative_to(SOURCE): hashlib.sha256(p.read_bytes()).hexdigest()
                   for p in SOURCE.rglob('*') if p.is_file()}
        program = '''import sys,json
sys.path.insert(0,sys.argv[1])
from src.pipeline import totals, labels
from src.bridge import run
rows=[{"enabled":False,"amount":"bad","label":"ab"},{"enabled":True,"amount":"2","label":"cat"},{"enabled":"yes","amount":"3.5","label":""}]
print(json.dumps({"total":totals(rows),"empty":totals([]),"labels":labels(rows),"bridge":run([-2,0,1,3])},sort_keys=True))'''
        outputs = []
        with tempfile.TemporaryDirectory() as temporary:
            for name, source in [('original', SOURCE), ('annotated', DETAIL)]:
                isolated = Path(temporary) / name
                shutil.copytree(source, isolated)
                env = os.environ.copy()
                env['PYTHONDONTWRITEBYTECODE'] = '1'
                run = subprocess.run([sys.executable, '-c', program, str(isolated)], cwd=isolated,
                                     env=env, capture_output=True, text=True)
                self.assertEqual(run.returncode, 0, run.stderr)
                outputs.append(json.loads(run.stdout))
        expected = {'total': 5.5, 'empty': 0, 'labels': ['ba', 'tac', ''], 'bridge': [0, 2, 6]}
        self.assertEqual(outputs, [expected, expected])
        self.assertEqual(initial, {p.relative_to(SOURCE): hashlib.sha256(p.read_bytes()).hexdigest()
                                   for p in SOURCE.rglob('*') if p.is_file()})

    def test_guides_coverage_and_relative_paths(self):
        for output in [SECTION, DETAIL]:
            metadata = output / '.code-explainer'
            for filename in ['guide.md', 'coverage.json', 'annotations.patch', 'checks.json']:
                self.assertTrue((metadata / filename).is_file())
            for row in json.loads((metadata / 'coverage.json').read_text()):
                self.assertIn(row['status'], ['examined', 'annotated', 'skipped', 'unresolved'])
                path = Path(row['output_path'])
                self.assertFalse(path.is_absolute())
                self.assertNotIn('..', path.parts)
                self.assertTrue((output / path).is_file())


class PackageContract(unittest.TestCase):
    def test_skill_metadata_and_relative_links(self):
        skill = ROOT / 'repo-code-explainer'
        content = (skill / 'SKILL.md').read_text()
        self.assertTrue(content.startswith('---\nname: repo-code-explainer\n'))
        self.assertIn('license: MIT\n', content.split('---', 2)[1])
        for markdown in skill.rglob('*.md'):
            for target in re.findall(r'\]\(([^)]+)\)', markdown.read_text()):
                if '://' not in target and not target.startswith('#'):
                    self.assertTrue((markdown.parent / target.split('#')[0]).is_file(), target)
        self.assertEqual((ROOT / 'LICENSE').read_bytes(), (skill / 'LICENSE').read_bytes())
        self.assertIn('MIT License', (ROOT / 'LICENSE').read_text())


if __name__ == '__main__':
    unittest.main()
