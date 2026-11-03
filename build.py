#!/usr/bin/env python3
"""Venusleeyous 博客生成器。

    python build.py              构建整站到 dist/
    python build.py serve        构建并在 http://localhost:8000 预览
    python build.py new <slug>   新建一篇文章草稿

文章放在 content/posts/*.md，站点文字在 site.yaml，页面模板在 templates/。
"""
import html
import json
import math
import re
import shutil
import sys
from collections import Counter, OrderedDict
from datetime import date, datetime, timezone
from email.utils import format_datetime
from pathlib import Path
from urllib.parse import quote

import markdown
import yaml
from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader, select_autoescape
from markdown.extensions.toc import TocExtension, slugify_unicode
from markdown.inlinepatterns import SimpleTagInlineProcessor
from pygments import lex
from pygments.lexers import TextLexer, get_lexer_by_name
from pygments.token import Comment, Generic, Keyword, Name, Number, String
from pygments.util import ClassNotFound

ROOT = Path(__file__).resolve().parent
CONTENT, TEMPLATES, PUBLIC, DIST = ROOT / "content", ROOT / "templates", ROOT / "public", ROOT / "dist"
WEEK_CN = "一二三四五六日"

# ---------------------------------------------------------------- markdown

# pygments token -> highlight.js class, so the existing stylesheet keeps working
HLJS = [
    (Comment.Preproc, "hljs-meta"), (Comment, "hljs-comment"),
    (Keyword.Constant, "hljs-literal"), (Keyword, "hljs-keyword"),
    (String, "hljs-string"), (Number, "hljs-number"),
    (Name.Builtin, "hljs-built_in"), (Name.Function, "hljs-title"), (Name.Class, "hljs-title"),
    (Name.Decorator, "hljs-meta"), (Name.Variable, "hljs-variable"),
    (Name.Tag, "hljs-tag"), (Name.Attribute, "hljs-attr"),
    (Generic.Prompt, "hljs-meta"), (Generic.Inserted, "hljs-addition"), (Generic.Deleted, "hljs-deletion"),
]
LEXER_ALIAS = {"shell": "bash", "sh": "bash", "zsh": "bash", "ps": "powershell", "py": "python", "vimrc": "vim"}


def highlight(code, lang):
    try:
        lexer = get_lexer_by_name(LEXER_ALIAS.get(lang, lang)) if lang else TextLexer()
    except ClassNotFound:
        lexer = TextLexer()
    out = []
    for ttype, value in lex(code, lexer):
        cls = next((c for t, c in HLJS if ttype in t), None)
        text = html.escape(value, quote=False)
        out.append(f'<span class="{cls}">{text}</span>' if cls and value.strip() else text)
    return "".join(out).rstrip("\n")


def code_block(soup, code_text, lang):
    label = lang or "plain"
    wrap = BeautifulSoup(
        f'<div class="code-block"><div class="code-meta"><span class="code-lang">{html.escape(label)}</span>'
        f'<button class="code-copy" type="button" aria-label="复制代码">复制</button></div>'
        f'<pre><code class="hljs language-{html.escape(label)}">{highlight(code_text, lang)}</code></pre></div>',
        "html.parser",
    )
    return wrap


def enhance(html_text):
    """Post-process rendered Markdown: code blocks, tab groups, external links."""
    soup = BeautifulSoup(html_text, "html.parser")
    for pre in soup.find_all("pre"):
        code = pre.find("code")
        if not code:
            continue
        lang = next((c[9:] for c in code.get("class", []) if c.startswith("language-")), "")
        pre.replace_with(code_block(soup, code.get_text(), lang))

    for n, tabs in enumerate(soup.select("div.tabs")):
        items = tabs.find_all("div", class_="tab-item", recursive=False)
        gid = f"tabs-{n + 1}"
        nav = "".join(
            f'<li class="tab{" active" if i == 0 else ""}"><button type="button">{html.escape(it.get("data-label", f"选项 {i + 1}"))}</button></li>'
            for i, it in enumerate(items)
        )
        panes = "".join(
            f'<div class="tab-item-content{" active" if i == 0 else ""}">{it.decode_contents()}</div>'
            for i, it in enumerate(items)
        )
        tabs.replace_with(BeautifulSoup(f'<div class="tabs" id="{gid}"><ul class="nav-tabs">{nav}</ul><div class="tab-contents">{panes}</div></div>', "html.parser"))

    for a in soup.find_all("a", href=True):
        if a["href"].startswith(("http://", "https://")):
            a["target"] = "_blank"
            a["rel"] = "noopener"
    return str(soup)


class Strikethrough(markdown.Extension):
    """~~删除线~~"""
    def extendMarkdown(self, md):
        md.inlinePatterns.register(SimpleTagInlineProcessor(r"(~{2})(.+?)~{2}", "del"), "del", 175)


def render_md(text):
    md = markdown.Markdown(extensions=[
        Strikethrough(), "fenced_code", "tables", "md_in_html", "sane_lists",
        TocExtension(slugify=slugify_unicode, permalink=False, toc_depth="2-4"),
    ])
    # tab groups are written as <div class="tabs"> / <div class="tab-item" data-label="…"> in Markdown
    text = re.sub(r'<div class="(tabs|tab-item)"([^>]*)>', r'<div class="\1"\2 markdown="1">', text)
    # Python-Markdown can't fence code inside "> " quotes; turn such quotes into an HTML block
    def quote_block(m):
        inner = re.sub(r"^> ?", "", m.group(0), flags=re.M)
        return f'<blockquote markdown="1">\n\n{inner}\n\n</blockquote>\n'
    text = re.sub(r"(?:^>.*\n?)+", lambda m: quote_block(m) if "```" in m.group(0) else m.group(0), text, flags=re.M)
    return enhance(md.convert(text))


def plain_text(html_text, keep_code=False):
    soup = BeautifulSoup(html_text, "html.parser")
    if not keep_code:
        for el in soup.select(".code-block"):
            el.decompose()
    return re.sub(r"\s+", " ", soup.get_text(" ")).strip()


def count_words(text):
    cjk = len(re.findall(r"[㐀-鿿豈-﫿]", text))
    latin = len(re.findall(r"[A-Za-z0-9_]+", text))
    return cjk + latin

# ---------------------------------------------------------------- content


def split_front(raw):
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", raw, re.S)
    if not m:
        raise ValueError("缺少 --- frontmatter ---")
    return yaml.safe_load(m.group(1)) or {}, m.group(2)


def load_posts():
    posts = []
    for path in sorted((CONTENT / "posts").glob("*.md")):
        meta, body = split_front(path.read_text(encoding="utf-8"))
        if meta.get("draft"):
            continue
        d = meta["date"]
        d = d if isinstance(d, date) else datetime.strptime(str(d), "%Y-%m-%d").date()
        html_body = render_md(body)
        words = count_words(plain_text(html_body, keep_code=True))
        text = plain_text(html_body)
        cats = meta.get("categories") or ["没事瞎写的"]
        posts.append({
            "slug": path.stem,
            "url": f"/posts/{path.stem}/",
            "title": meta["title"],
            "date": d,
            "categories": cats if isinstance(cats, list) else [cats],
            "tags": meta.get("tags") or [],
            "source": meta.get("source") or "",
            "description": meta.get("description", ""),
            "cover": meta.get("cover") or "/assets/img/bg5.jpg",
            "html": html_body,
            "text": text,
            "words": words,
            "minutes": max(2, round(len(text) / 330)),  # 正文字数估算，代码不计入
        })
    posts.sort(key=lambda p: (p["date"], p["slug"]), reverse=True)
    return posts

# ---------------------------------------------------------------- helpers


def dot(d):
    return d.strftime("%Y.%m.%d")


def cn_date(d):
    return f"{d.year} 年 {d.month} 月 {d.day} 日"


def qurl(s):
    return quote(str(s), safe="")


def fmt(s, **kw):
    for k, v in kw.items():
        s = s.replace("{" + k + "}", str(v))
    return s


def kfmt(n):
    return f"{n / 1000:.1f}k" if n >= 1000 else str(n)


SPARE_COLORS = ["#2357C6", "#2E8B57", "#C98A12", "#C4423A", "#7462B0", "#1F8A8A"]


def month_add(d, n):
    m = d.month - 1 + n
    return date(d.year + m // 12, m % 12 + 1, 1)


def genome_track(posts, categories):
    """首页的"基因组轨道"：横轴是时间，一行一个分类，每篇文章是一个色块。"""
    if not posts:
        return None
    start = date(posts[-1]["date"].year, posts[-1]["date"].month, 1)
    end = month_add(posts[0]["date"], 1)
    span = (end - start).days or 1
    months = (end.year - start.year) * 12 + end.month - start.month
    step = 1 if months <= 18 else (3 if months <= 48 else 12)

    def x(d):
        return round((d - start).days / span * 100, 2)

    ticks, t = [], start
    while t <= end:
        if step == 12 and t.month != 1 and t != start:
            t = date(t.year + 1, 1, 1)
            continue
        ticks.append({"x": x(t), "label": f"{t.year}" if step == 12 else f"{t.year}.{t.month:02d}"})
        t = month_add(t, step)
    rows = [{"name": c["name"], "color": c["color"],
             "items": [{"post": p, "x": x(p["date"])} for p in c["posts"]]} for c in categories]
    return {"ticks": ticks, "rows": rows,
            "from": posts[-1]["date"], "to": posts[0]["date"]}


PROJECT_COLORS = ["#1F8A8A", "#7462B0", "#C4423A", "#C98A12", "#2357C6", "#2E8B57"]


def ym(s):
    y, m = str(s).split("-")[:2]
    return date(int(y), int(m), 1)


def load_projects():
    """content/projects.yaml -> 分组的项目列表，以及按年份画的项目轨道。"""
    path = CONTENT / "projects.yaml"
    if not path.exists():
        return None
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    groups = data.get("groups") or []
    items = [it for g in groups for it in g["items"]]
    if not items:
        return None
    start = date(min(ym(it["since"]) for it in items).year, 1, 1)
    end = date(max(ym(it["updated"]) for it in items).year + 1, 1, 1)
    span = (end - start).days

    def x(d):
        return round((d - start).days / span * 100, 2)

    for gi, g in enumerate(groups):
        g["color"] = g.get("color") or PROJECT_COLORS[gi % len(PROJECT_COLORS)]
        g["items"].sort(key=lambda it: str(it["updated"]), reverse=True)
        for it in g["items"]:
            it["url"] = it.get("url") or f"https://github.com/liqiming-whu/{it['repo']}"
            a, b = ym(it["since"]), month_add(ym(it["updated"]), 1)
            it["x"], it["w"] = x(a), max(round(x(b) - x(a), 2), 0.8)
            it["color"] = g["color"]
            it["span"] = it["since"].replace("-", ".") if it["since"] == it["updated"] else f'{it["since"].replace("-", ".")}–{it["updated"].replace("-", ".")}'
    ticks = [{"x": x(date(y, 1, 1)), "label": str(y)} for y in range(start.year, end.year + 1)]
    recent = sorted(items, key=lambda it: str(it["updated"]), reverse=True)
    return {"groups": groups, "ticks": ticks, "recent": recent, "early": data.get("early") or []}


def load_resume():
    path = CONTENT / "resume.yaml"
    if not path.exists():
        return None
    r = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    me = r.get("me", "")
    for p in r.get("papers") or []:
        names = [a.strip() for a in str(p["authors"]).split(",")]
        p["authors_html"] = ", ".join(
            f"<strong>{html.escape(n)}</strong>" if n.rstrip("#*") == me else html.escape(n) for n in names)
        p["co_first"] = any(n.rstrip("*").endswith("#") and n.rstrip("#*") == me for n in names)
    r["papers"] = sorted(r.get("papers") or [], key=lambda p: p["year"], reverse=True)
    for sk in r.get("skills") or []:
        sk["html"] = re.sub(r"^<p>|</p>$", "", render_md(sk["text"]).strip())
    return r


def group_tags(tags, groups):
    by_name = {t["name"]: t for t in tags}
    out, used = [], set()
    for gname, names in groups.items():
        members = [by_name[n] for n in names if n in by_name and n not in used]
        used.update(t["name"] for t in members)
        if members:
            out.append({"name": gname, "tags": members})
    rest = [t for t in tags if t["name"] not in used]
    if rest:
        other = next((g for g in out if g["name"] == "其他"), None)
        if other:
            other["tags"] += rest
        else:
            out.append({"name": "其他", "tags": rest})
    return out


def build():
    site = yaml.safe_load((ROOT / "site.yaml").read_text(encoding="utf-8"))
    posts = load_posts()

    cat_count = Counter(c for p in posts for c in p["categories"])
    tag_count = Counter(t for p in posts for t in p["tags"])
    # keep the order from site.yaml, then any new category by size
    cat_order = [c for c in site.get("categories", {}) if c in cat_count]
    cat_order += [c for c, _ in cat_count.most_common() if c not in cat_order]
    cat_conf = site.get("categories", {})
    categories = [{
        "name": c, "count": cat_count[c],
        "desc": (cat_conf.get(c) or {}).get("desc", ""),
        "color": (cat_conf.get(c) or {}).get("color") or SPARE_COLORS[i % len(SPARE_COLORS)],
        "posts": [p for p in posts if c in p["categories"]],
    } for i, c in enumerate(cat_order)]
    color_of = {c: (v or {}).get("color") for c, v in cat_conf.items() if (v or {}).get("color")}
    color_of.update({c["name"]: c["color"] for c in categories})
    track = genome_track(posts, categories)
    tags = [{"name": t, "count": n, "posts": [p for p in posts if t in p["tags"]]} for t, n in tag_count.most_common()]
    tag_groups = group_tags(tags, site.get("tag_groups") or {})
    projects = load_projects()

    archive = OrderedDict()
    for p in posts:
        archive.setdefault(p["date"].year, OrderedDict()).setdefault(p["date"].month, []).append(p)

    oldest = posts[-1]["date"] if posts else date.today()
    stats = {
        "posts": len(posts), "categories": len(categories), "tags": len(tags),
        "words": kfmt(sum(p["words"] for p in posts)),
        "updated": dot(posts[0]["date"]) if posts else "",
        "start": f"{oldest.year} 年 {oldest.month} 月",
        "projects": sum(len(g["items"]) for g in projects["groups"]) if projects else 0,
    }

    env = Environment(loader=FileSystemLoader(TEMPLATES), autoescape=select_autoescape(["html", "xml"]),
                      trim_blocks=True, lstrip_blocks=True)
    env.filters.update(dot=dot, cn_date=cn_date, qurl=qurl, truncate_text=lambda s, n=400: s[:n])
    env.globals.update(site=site, stats=stats, categories=categories, tags=tags, fmt=fmt, year=date.today().year,
                       color_of=color_of, track=track, tag_groups=tag_groups, projects=projects)

    if DIST.exists():
        shutil.rmtree(DIST)
    shutil.copytree(PUBLIC, DIST)

    def write(rel, template, **ctx):
        out = DIST / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(env.get_template(template).render(**ctx), encoding="utf-8")

    write("index.html", "index.html", page="home", posts=posts)
    write("articles.html", "articles.html", page="articles", posts=posts)
    write("ai-rankings.html", "ai-rankings.html", page="ai_rankings",
          posts=[p for p in posts if "AI 排行榜" in p["categories"]])
    write("archives.html", "archives.html", page="archives", archive=archive)
    write("categories.html", "categories.html", page="categories")
    write("tags.html", "tags.html", page="tags")
    write("about.html", "about.html", page="about",
          about_html=render_md((CONTENT / "about.md").read_text(encoding="utf-8")))
    write("links.html", "links.html", page="links")
    resume = load_resume()
    if resume and projects:
        by_repo = {it["repo"]: it for g in projects["groups"] for it in g["items"]}
        resume["featured"] = [by_repo[r] for r in resume.get("featured_projects") or [] if r in by_repo]
    if resume:
        write("resume.html", "resume.html", page="resume", resume=resume)
    if projects:
        write("projects.html", "projects.html", page="projects")
    write("message.html", "message.html", page="message")
    write("404.html", "404.html", page="404")

    for i, p in enumerate(posts):
        older = posts[i + 1] if i + 1 < len(posts) else None
        newer = posts[i - 1] if i > 0 else None
        same = [q for q in posts if q is not p and set(q["categories"]) & set(p["categories"])]
        rest = [q for q in posts if q is not p and q not in same]
        write(f"posts/{p['slug']}/index.html", "post.html", page="post", post=p,
              prev=older, next=newer, related=(same + rest)[:3])

    search = [{
        "title": p["title"], "url": p["url"], "date": p["date"].isoformat(),
        "categories": p["categories"], "tags": p["tags"], "excerpt": p["description"],
        "cover": p["cover"], "color": color_of.get(p["categories"][0], ""), "text": p["text"],
    } for p in posts]
    (DIST / "search.json").write_text(json.dumps(search, ensure_ascii=False), encoding="utf-8")

    def rfc822(d):
        return format_datetime(datetime(d.year, d.month, d.day, tzinfo=timezone.utc))
    write("rss.xml", "rss.xml", posts=posts[:20], rfc822=rfc822, now=rfc822(date.today()))

    print(f"✓ 已生成 {len(posts)} 篇文章 → {DIST.relative_to(ROOT)}/")


def new_post(slug):
    path = CONTENT / "posts" / f"{slug}.md"
    if path.exists():
        sys.exit(f"{path} 已经存在")
    path.write_text(
        f"---\ntitle: 新文章标题\ndate: {date.today().isoformat()}\ncategories: [python]\ntags: [造轮子]\n"
        f"description: 一句话介绍这篇文章，会显示在卡片和搜索结果里。\ncover: /assets/img/bg5.jpg\n"
        f"draft: true   # 写完删掉这一行就会发布\n---\n\n正文从这里开始。\n",
        encoding="utf-8",
    )
    print(f"✓ 新建 {path.relative_to(ROOT)}")


def serve():
    import functools
    import http.server
    build()
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(DIST))
    print("预览：http://localhost:8000  （Ctrl C 退出）")
    http.server.ThreadingHTTPServer(("127.0.0.1", 8000), handler).serve_forever()


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "build"
    if cmd == "build":
        build()
    elif cmd == "serve":
        serve()
    elif cmd == "new" and len(sys.argv) > 2:
        new_post(sys.argv[2])
    else:
        sys.exit(__doc__)
