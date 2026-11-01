"""Safety tests for generate_docs.py: catalog data must not become MDX code or paths.

Run from the repo root:  python3 -m unittest discover -s tests
"""
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import generate_docs as g  # noqa: E402


def product(**over):
    p = {"name": "Fixture", "slug": "fixture", "category": ["Sensors"], "description": {"technical": "ok", "consumer": "ok"}}
    p.update(over)
    return p


class MdxEscaping(unittest.TestCase):
    def test_code_significant_characters_become_entities(self):
        out = g.mdx_text("x {globalThis.a=1} <Evil onClick=\"y\"/> z")
        for ch in "{}<>":
            self.assertNotIn(ch, out)

    def test_line_leading_import_export_is_neutralised(self):
        out = g.mdx_text("intro\nexport const m = 1\n  import fs from 'fs'")
        self.assertNotRegex(out, r"(?m)^\s*(import|export)\b")
        self.assertIn("&#101;xport const m = 1", out)

    def test_plain_markdown_is_unchanged(self):
        s = "Works with **Zigbee 3.0**.\n\n- item one\n- item two"
        self.assertEqual(g.mdx_text(s), s)

    def test_non_string_field_is_rejected(self):
        with self.assertRaises(TypeError):
            g.mdx_text(["a"])

    def test_table_cell_pipe_cannot_split_cell(self):
        self.assertNotIn("|", g.mdx_safe("a | b"))

    def test_product_page_neutralises_every_interpolated_field(self):
        evil = "{String(1+1)} <X/>\nexport const e = 1"
        page = g.product_page(
            product(
                name='Bad "name" {x}\n---\ninjected: yes',
                limitations=evil,
                dependencies=evil,
                protocol=evil,
                device_type=evil,
                description={"technical": evil, "consumer": evil},
                specs={"channels": evil, "summary": "{k}: {v}"},
                pricing={"gst_rate": "18{x}", "hsn": "<8536>"},
            ),
            "sensors",
        )
        body = page.split("\n---\n", 1)[1]  # everything after the frontmatter block
        self.assertNotRegex(body, r"(?m)^\s*(import|export)\b")
        self.assertNotIn("{String(1+1)}", body)
        self.assertNotIn("<X/>", body)
        # Only generator-authored tags may remain.
        import re
        tags = set(re.findall(r"<(/?[A-Za-z]+)", body))
        self.assertTrue(tags <= {"Callout", "/Callout"}, tags)

    def test_frontmatter_cannot_be_broken_out_of(self):
        page = g.product_page(product(name='A"\n---\ninjected: yes'), "sensors")
        front = page.split("\n---\n", 1)[0]
        self.assertEqual(front.count("\n"), 2)  # '---', title, description only
        self.assertNotIn("injected: yes\n", page.split("\n---\n")[1] if page.count("\n---\n") > 1 else "")

    def test_category_card_attributes_are_escaped(self):
        idx = g.category_index("sensors", "Sensors", [product(name='x" onClick={1}', description={"consumer": "{y}"})])
        self.assertNotIn("{1}", idx)
        self.assertNotIn("{y}", idx)
        self.assertNotIn('" onClick', idx)


class SlugAndPaths(unittest.TestCase):
    def test_traversal_and_absolute_slugs_rejected(self):
        for bad in ["../../smartify-pro/x", "/etc/x", "a/b", "..", ".hidden", "Upper", "a b", "index", "x.mdx"]:
            with self.assertRaises(ValueError, msg=bad):
                g.product_slug(product(slug=bad))

    def test_real_style_slugs_accepted(self):
        for ok in ["fixture", "ir-blaster-w--analog-screen-temp-and-humidity-sensor-wifi", "led-controller-cv-rgbpluscct"]:
            self.assertEqual(g.product_slug(product(slug=ok)), ok)

    def test_missing_slug_falls_back_to_slugified_name(self):
        self.assertEqual(g.product_slug({"name": "Reach IR Pro"}), "reach-ir-pro")

    def test_write_file_refuses_paths_outside_docs_dir(self):
        with tempfile.TemporaryDirectory() as t:
            docs = Path(t) / "content" / "docs"
            docs.mkdir(parents=True)
            with mock.patch.object(g, "DOCS_DIR", docs), mock.patch.object(g, "SCRIPT_DIR", Path(t)):
                g.write_file(docs / "products" / "ok.mdx", "x")
                self.assertTrue((docs / "products" / "ok.mdx").exists())
                with self.assertRaises(ValueError):
                    g.write_file(docs / "products" / ".." / ".." / ".." / "escape.mdx", "x")
                self.assertFalse((Path(t) / "escape.mdx").exists())


class ImageCopy(unittest.TestCase):
    def test_symlinked_png_is_not_copied(self):
        with tempfile.TemporaryDirectory() as t:
            t = Path(t)
            (t / "src").mkdir()
            (t / "secret.txt").write_text("DUMMY-MARKER")
            (t / "src" / "real.png").write_bytes(b"\x89PNG-real")
            (t / "src" / "link.png").symlink_to(t / "secret.txt")
            copied, skipped = g.copy_images(t / "src", t / "out")
            self.assertEqual((copied, skipped), (1, 1))
            self.assertTrue((t / "out" / "real.png").exists())
            self.assertFalse((t / "out" / "link.png").exists())


if __name__ == "__main__":
    unittest.main()
