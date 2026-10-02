"""Regressions for the actual Markdown/TeX corruption modes, not just counts."""

import unittest
import json
import tempfile
from pathlib import Path

from math_rendering import (
    ALIASES, CASES, REGISTRY, TRAINING, check_corpus, check_rendering,
    convert_legacy, fingerprint, formulas, to_arithmatex,
)
import mkdocs_math


class PreservationTests(unittest.TestCase):
    def test_code_and_front_matter_untouched(self):
        text = '---\nexample: "\\(x\\)"\n---\n~~~md\n\\[\nx\n\\]\n~~~\n`\\(y\\)`\n\\(z\\)\n'
        candidate = convert_legacy(text, 'example.md')
        self.assertEqual(len(formulas(candidate)), 1)
        self.assertEqual(fingerprint(text, 'example.md'), fingerprint(candidate, 'example.md'))
        self.assertIn('`\\(y\\)`', to_arithmatex(candidate))
        self.assertTrue(to_arithmatex(candidate).endswith('\\(z\\)\n'))

    def test_operator_and_prose_mutations_rejected(self):
        original = 'Claim\n\\[\nP(x)\n>\nP(y)\n\\]\n'
        candidate = convert_legacy(original, 'example.md')
        baseline = fingerprint(original, 'example.md')
        self.assertEqual(baseline, fingerprint(candidate, 'example.md'))
        for changed in (candidate.replace('>', '<'), candidate.replace('Claim', 'Changed'), candidate.replace('P(y)', 'P(z)')):
            self.assertNotEqual(baseline, fingerprint(changed, 'example.md'))
        rendered = check_rendering(candidate)
        self.assertNotIn('<blockquote>', rendered)
        self.assertIn('&gt;', rendered)

    def test_table_bars_norm_and_braces_survive(self):
        original = '| Name | Math |\n| --- | --- |\n' + ''.join('| x | \\(' + body + '\\) |\n' for body in [*ALIASES, r'M\subset\{1,\ldots,T\}'])
        candidate = convert_legacy(original, REGISTRY)
        self.assertEqual(fingerprint(original, REGISTRY), fingerprint(candidate, REGISTRY))
        rendered = check_rendering(candidate)
        self.assertEqual(rendered.count('<td>'), 8)
        for body in ALIASES.values():
            self.assertIn(body, rendered)
        self.assertIn(r'\{1,\ldots,T\}', rendered)
        self.assertNotEqual(fingerprint(candidate, REGISTRY), fingerprint(candidate.replace(r'\Vert', r'\vert'), REGISTRY))

    def test_four_cases_exceptions_preserve_row_breaks(self):
        for body in CASES:
            text = r'\[' + body + '\\]\n'
            candidate = convert_legacy(text, TRAINING)
            self.assertTrue(candidate.startswith('$$'))
            self.assertEqual(formulas(candidate)[0].body, body)
            check_rendering(candidate)
            with self.assertRaises(ValueError):
                convert_legacy(text, 'other.md')

    def test_unexpected_structures_fail_closed(self):
        for text in ('\\[\nx\n', '\\(x\n', '\\[ x \\]\n', '\\]\n', '```python\nx\n', '---\nx\n', '$$\nx\n', '$`x\n'):
            with self.subTest(text=text), self.assertRaises(ValueError):
                formulas(text)

    def test_native_html_transport_preserves_less_than_and_ampersand(self):
        # The native fence formatter emits raw HTML, so <T would otherwise
        # become an HTML element and &lt; could become an unintended operator.
        source = '```math\nn<T & x>0 & \\text{&lt;}\n```\n'
        rendered = check_rendering(source)
        self.assertIn('n&lt;T &amp; x&gt;0', rendered)
        self.assertIn('&amp;lt;', rendered)

    def test_gate_rejects_source_and_wrapper_regressions(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'scripts').mkdir()
            source = 'Claim\n\n```math\nx>y\n```\n'
            (root / 'scripts/math-preservation.json').write_text(json.dumps({'files': {'example.md': fingerprint(source, 'example.md')}}), encoding='utf-8')
            path = root / 'example.md'
            path.write_bytes(source.encode('utf-8'))
            self.assertEqual(check_corpus(root), [])
            for mutation in (source.replace('>', '<'), source.replace('Claim', 'Changed'), source.replace('```math', r'\[').replace('```', r'\]')):
                path.write_bytes(mutation.encode('utf-8'))
                self.assertTrue(check_corpus(root))

    def test_reviewed_corpus_and_every_native_render(self):
        root = Path(__file__).resolve().parents[1]
        self.assertEqual(check_corpus(root), [])
        count = 0
        for path in sorted((root / 'docs').glob('*/*.md')):
            with self.subTest(file=path.name, locale=path.parent.name):
                text = path.read_bytes().decode('utf-8')
                check_rendering(text)
                count += len(formulas(text))
        self.assertEqual(count, 2775)


class HookTests(unittest.TestCase):
    def test_hook_uses_native_generic_fence_and_preserves_code(self):
        import markdown
        config = {'markdown_extensions': ['tables'], 'mdx_configs': {}}
        mkdocs_math.on_config(config)
        source = '`$`x`$`\n\n$`x\\{y\\}`$\n\n```math\na>b\n```\n'
        # Code example uses a longer fence around the literal protected syntax.
        source = source.replace('`$`x`$`', '``$`x`$``')
        adapted = mkdocs_math.on_page_markdown(source)
        self.assertTrue(adapted.startswith('``$`x`$``'))
        rendered = markdown.markdown(adapted, extensions=config['markdown_extensions'], extension_configs=config['mdx_configs'])
        self.assertEqual(rendered.count('class="arithmatex"'), 2)
        self.assertIn('a&gt;b', rendered)


if __name__ == '__main__':
    unittest.main()
