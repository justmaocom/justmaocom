"""Rewrite the recent-posts block in README.md from the justmao.com Atom feed. Standard library only."""
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

FEED = "https://justmao.com/en/feed.xml"
README = Path(__file__).resolve().parent.parent / "README.md"
START, END = "<!-- posts:start -->", "<!-- posts:end -->"
ATOM = "{http://www.w3.org/2005/Atom}"
LIMIT = 5


def parse(xml_text):
    """Return [(date, title, url)] newest first, keeping only https links on justmao.com."""
    posts = []
    for entry in ET.fromstring(xml_text).iter(ATOM + "entry"):
        title = (entry.findtext(ATOM + "title") or "").strip()
        url = next((l.get("href", "") for l in entry.iter(ATOM + "link") if l.get("rel", "alternate") == "alternate"), "")
        try:
            when = datetime.fromisoformat(entry.findtext(ATOM + "published") or entry.findtext(ATOM + "updated") or "")
        except ValueError:
            continue
        if title and url.startswith("https://justmao.com/"):
            posts.append((when, title, url))
    # sort on the full timestamp so same-day posts keep publish order
    posts.sort(key=lambda p: p[0], reverse=True)
    return [(w.date().isoformat(), t, u) for w, t, u in posts[:LIMIT]]


def render(posts):
    # escape markdown/HTML so a title can't break the list or inject markup
    esc = lambda s: re.sub(r"([\\`*_\[\]|])", r"\\\1", s).replace("<", "&lt;").replace(">", "&gt;")
    return "\n".join(f"- [{esc(t)}]({u.replace(')', '%29')}) · {d}" for d, t, u in posts)


def replace_block(readme, body):
    pattern = re.compile(re.escape(START) + r".*?" + re.escape(END), re.S)
    if not pattern.search(readme):
        raise ValueError("README is missing the posts markers")
    return pattern.sub(lambda _: f"{START}\n{body}\n{END}", readme, count=1)


def main():
    req = urllib.request.Request(FEED, headers={"User-Agent": "readme-posts-updater"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        posts = parse(resp.read())
    if not posts:
        sys.exit("feed returned no usable posts; leaving README untouched")
    README.write_text(replace_block(README.read_text(encoding="utf-8"), render(posts)), encoding="utf-8")


if __name__ == "__main__":
    main()
