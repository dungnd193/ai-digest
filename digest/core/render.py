from __future__ import annotations

import yaml

from digest.core.content_types import BlogPost


def render_post(post: BlogPost, *, draft: bool = False) -> str:
    """Serialize a BlogPost to Hugo Markdown: YAML front-matter + CommonMark body.
    No Hugo shortcodes are emitted — content stays portable to other generators."""
    front_matter = {
        "title": post.title,
        "date": post.date,
        "lang": post.lang,
        "slug": post.slug,
        "categories": [post.category],
        "tags": list(post.tags),
        "summary": post.summary,
        "draft": draft,
    }
    fm = yaml.safe_dump(front_matter, allow_unicode=True, sort_keys=False)
    return f"---\n{fm}---\n\n{post.body}\n"


def post_filename(post: BlogPost) -> str:
    """Hugo multilingual filename: <date>-<slug>.<lang>.md."""
    return f"{post.date}-{post.slug}.{post.lang}.md"
