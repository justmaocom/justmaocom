import unittest

from update_posts import END, START, parse, render, replace_block

FEED = """<feed xmlns="http://www.w3.org/2005/Atom">
<entry><title>Older</title><link href="https://justmao.com/en/posts/older/" rel="alternate"/><published>2026-11-01T17:00:00+08:00</published></entry>
<entry><title>Use [brackets] | *stars* &lt;b&gt;</title><link href="https://justmao.com/en/posts/new/" rel="alternate"/><published>2026-11-19T17:00:00+08:00</published></entry>
<entry><title>Same day, earlier</title><link href="https://justmao.com/en/posts/morning/" rel="alternate"/><published>2026-11-19T09:30:00+08:00</published></entry>
<entry><title>Elsewhere</title><link href="http://evil.example/x" rel="alternate"/><published>2026-11-20T17:00:00+08:00</published></entry>
</feed>"""


class UpdatePostsTest(unittest.TestCase):
    def test_parse_sorts_newest_first_and_drops_foreign_links(self):
        posts = parse(FEED)
        self.assertEqual([p[2].split("/")[-2] for p in posts], ["new", "morning", "older"])
        self.assertEqual(posts[0][0], "2026-11-19")

    def test_render_escapes_markdown_and_html(self):
        line = render(parse(FEED)[:1])
        self.assertEqual(line, r"- [Use \[brackets\] \| \*stars\* &lt;b&gt;](https://justmao.com/en/posts/new/) · 2026-11-19")

    def test_replace_block_only_touches_markers(self):
        readme = f"intro\n{START}\nold\n{END}\noutro\n"
        self.assertEqual(replace_block(readme, "- new"), f"intro\n{START}\n- new\n{END}\noutro\n")

    def test_missing_markers_raise(self):
        with self.assertRaises(ValueError):
            replace_block("no markers here", "- new")


if __name__ == "__main__":
    unittest.main()
