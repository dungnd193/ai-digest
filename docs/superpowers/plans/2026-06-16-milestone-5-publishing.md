# Milestone 5: Publishing + CI/CD — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: subagent-driven-development / executing-plans. Checkbox steps. TDD for Python tasks; for the Hugo/CI tasks, verification is "the site builds". Commit per task with the `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>` trailer.

**Goal:** Serialize `BlogPost`s to generator-neutral Hugo Markdown, write them into a Hugo site (homepage grouped by day, EN/VI i18n, category/tag taxonomy), commit/push to git, and auto-deploy to GitHub Pages via GitHub Actions.

**Architecture:** `render_post` turns a `BlogPost` into `---`-fenced YAML front-matter + the CommonMark body (no Hugo shortcodes — keeps content portable). `Publisher` writes files into `site/content/posts/` using Hugo's `<date>-<slug>.<lang>.md` multilingual filename convention, then commits and pushes (tolerant of push failures — content is never lost). The Hugo site uses minimal hand-written layouts (no external theme) so there's nothing to vendor. A GitHub Actions workflow builds `site/` and deploys to Pages on every push that touches it.

**Tech Stack:** Python 3.14, `uv`, `pytest`, `PyYAML`. Hugo (extended) installed locally to `~/.local/bin` for build verification. GitHub Actions + Pages.

---

## Conventions
- Repo root `~/Desktop/Workspace/ai-digest`, branch `feat/milestones`.
- `export PATH="$HOME/.local/bin:$PATH"` before `uv` and `hugo`.
- Python tests use tmp dirs and mocked subprocess — no real git push, no network.

## File structure
```
digest/
├── core/render.py            # render_post + post_filename
├── agents/publisher.py       # Publisher (write files + git)
└── tests/ test_render.py  test_publisher.py
site/
├── hugo.toml
├── content/posts/.gitkeep
├── i18n/en.toml  i18n/vi.toml
└── layouts/
    ├── _default/baseof.html  _default/single.html  _default/list.html
    └── index.html
.github/workflows/deploy.yml
```

---

## Task 1: render_post + post_filename

**Files:** Create `digest/core/render.py`; Test `digest/tests/test_render.py`

- [ ] **Step 1: Failing tests** `digest/tests/test_render.py`:
```python
import yaml

from digest.core.content_types import BlogPost
from digest.core.render import post_filename, render_post


def _post(lang="en"):
    return BlogPost(
        lang=lang, title='AI: "Agents" & more', slug="ai-agents",
        date="2026-06-16", category="Tools", tags=("ai", "llm"),
        summary="A summary.", body="# Heading\n\nBody text.",
        sources=("https://a.com",),
    )


def _split_front_matter(text):
    assert text.startswith("---\n")
    _, fm, body = text.split("---\n", 2)
    return yaml.safe_load(fm), body


def test_render_post_front_matter_fields():
    fm, body = _split_front_matter(render_post(_post()))
    assert fm["title"] == 'AI: "Agents" & more'
    assert fm["date"] == "2026-06-16"
    assert fm["lang"] == "en"
    assert fm["slug"] == "ai-agents"
    assert fm["categories"] == ["Tools"]
    assert fm["tags"] == ["ai", "llm"]
    assert fm["draft"] is False
    assert "Body text." in body


def test_render_post_draft_flag():
    fm, _ = _split_front_matter(render_post(_post(), draft=True))
    assert fm["draft"] is True


def test_post_filename_uses_date_slug_lang():
    assert post_filename(_post("en")) == "2026-06-16-ai-agents.en.md"
    assert post_filename(_post("vi")) == "2026-06-16-ai-agents.vi.md"
```

- [ ] **Step 2: Run → fail.**

- [ ] **Step 3: Implement** `digest/core/render.py`:
```python
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
```

- [ ] **Step 4: Run → pass** (3 passed). **Step 5: Commit** `feat: render BlogPost to Hugo markdown`.

---

## Task 2: Publisher — write files

**Files:** Create `digest/agents/publisher.py`; Test `digest/tests/test_publisher.py`

- [ ] **Step 1: Failing tests** `digest/tests/test_publisher.py`:
```python
from pathlib import Path

from digest.agents.publisher import Publisher
from digest.core.content_types import BlogPost


def _post(lang="en", slug="ai-agents"):
    return BlogPost(
        lang=lang, title="T", slug=slug, date="2026-06-16", category="Tools",
        tags=("ai",), summary="s", body="Body.", sources=("https://a.com",),
    )


def test_write_posts_creates_files(tmp_path):
    pub = Publisher(site_dir=tmp_path)
    paths = pub.write_posts([_post("en"), _post("vi")])
    assert len(paths) == 2
    posts_dir = tmp_path / "content" / "posts"
    assert (posts_dir / "2026-06-16-ai-agents.en.md").exists()
    assert (posts_dir / "2026-06-16-ai-agents.vi.md").exists()


def test_write_posts_content_has_front_matter(tmp_path):
    pub = Publisher(site_dir=tmp_path)
    [path] = pub.write_posts([_post("en")])
    text = Path(path).read_text(encoding="utf-8")
    assert text.startswith("---\n")
    assert "title:" in text
    assert "Body." in text


def test_write_posts_draft_sets_flag(tmp_path):
    pub = Publisher(site_dir=tmp_path)
    [path] = pub.write_posts([_post("en")], draft=True)
    assert "draft: true" in Path(path).read_text(encoding="utf-8")
```

- [ ] **Step 2: Run → fail.**

- [ ] **Step 3: Implement** `digest/agents/publisher.py`:
```python
from __future__ import annotations

import logging
import subprocess
from pathlib import Path

from digest.core.content_types import BlogPost
from digest.core.render import post_filename, render_post

logger = logging.getLogger(__name__)


class Publisher:
    """Writes blog posts into a Hugo site dir and commits/pushes them.
    File-writing and git are separate methods so each is independently testable."""

    def __init__(self, site_dir: str | Path, posts_subdir: str = "content/posts") -> None:
        self.site_dir = Path(site_dir)
        self.posts_dir = self.site_dir / posts_subdir

    def write_posts(self, posts: list[BlogPost], *, draft: bool = False) -> list[Path]:
        self.posts_dir.mkdir(parents=True, exist_ok=True)
        written: list[Path] = []
        for post in posts:
            path = self.posts_dir / post_filename(post)
            path.write_text(render_post(post, draft=draft), encoding="utf-8")
            written.append(path)
        return written
```

- [ ] **Step 4: Run → pass** (3 passed). **Step 5: Commit** `feat: Publisher writes Hugo post files`.

---

## Task 3: Publisher — git commit & push (tolerant)

**Files:** Modify `digest/agents/publisher.py` (add method); Test append to `digest/tests/test_publisher.py`

Behavior: `commit_and_push(message, repo_dir=None, remote="origin", push=True, retries=2)` runs `git add -A`, `git commit -m`, and optionally `git push` via subprocess in the repo dir (defaults to `site_dir`'s repo root = the project root). Returns True on success. If `git commit` reports nothing to commit, returns False (no error). If `git push` fails, retries then logs and returns False — files remain committed locally (never lost).

- [ ] **Step 1: Failing tests** — append to `digest/tests/test_publisher.py`:
```python
from unittest.mock import MagicMock, patch


def _completed(returncode=0, stdout="", stderr=""):
    m = MagicMock()
    m.returncode = returncode
    m.stdout = stdout
    m.stderr = stderr
    return m


def test_commit_and_push_happy_path(tmp_path):
    pub = Publisher(site_dir=tmp_path)
    with patch("digest.agents.publisher.subprocess.run", return_value=_completed(0)) as run:
        ok = pub.commit_and_push("msg", repo_dir=tmp_path)
    assert ok is True
    cmds = [c.args[0][:2] for c in run.call_args_list]
    assert ["git", "add"] in cmds
    assert ["git", "commit"] in cmds
    assert ["git", "push"] in cmds


def test_commit_and_push_nothing_to_commit_returns_false(tmp_path):
    pub = Publisher(site_dir=tmp_path)

    def fake_run(cmd, **kw):
        if cmd[:2] == ["git", "commit"]:
            return _completed(1, stdout="nothing to commit, working tree clean")
        return _completed(0)

    with patch("digest.agents.publisher.subprocess.run", side_effect=fake_run):
        ok = pub.commit_and_push("msg", repo_dir=tmp_path)
    assert ok is False


def test_commit_and_push_push_failure_retries_then_false(tmp_path):
    pub = Publisher(site_dir=tmp_path)

    def fake_run(cmd, **kw):
        if cmd[:2] == ["git", "push"]:
            return _completed(1, stderr="network error")
        return _completed(0)

    with patch("digest.agents.publisher.subprocess.run", side_effect=fake_run) as run:
        ok = pub.commit_and_push("msg", repo_dir=tmp_path, retries=2)
    assert ok is False
    push_calls = [c for c in run.call_args_list if c.args[0][:2] == ["git", "push"]]
    assert len(push_calls) == 3  # initial + 2 retries


def test_commit_and_push_skip_push(tmp_path):
    pub = Publisher(site_dir=tmp_path)
    with patch("digest.agents.publisher.subprocess.run", return_value=_completed(0)) as run:
        ok = pub.commit_and_push("msg", repo_dir=tmp_path, push=False)
    assert ok is True
    assert not any(c.args[0][:2] == ["git", "push"] for c in run.call_args_list)
```

- [ ] **Step 2: Run → fail.**

- [ ] **Step 3: Implement** — add to `Publisher` (and `import time` at top):
```python
    def commit_and_push(
        self,
        message: str,
        *,
        repo_dir: str | Path | None = None,
        remote: str = "origin",
        push: bool = True,
        retries: int = 2,
    ) -> bool:
        cwd = str(repo_dir or self.site_dir)

        self._git(["git", "add", "-A"], cwd)
        commit = self._git(["git", "commit", "-m", message], cwd)
        if commit.returncode != 0:
            if "nothing to commit" in (commit.stdout + commit.stderr).lower():
                logger.info("nothing to commit")
                return False
            logger.warning("git commit failed: %s", commit.stderr.strip())
            return False

        if not push:
            return True

        for attempt in range(retries + 1):
            pushed = self._git(["git", "push", remote], cwd)
            if pushed.returncode == 0:
                return True
            logger.warning("git push attempt %d failed: %s", attempt + 1, pushed.stderr.strip())
            if attempt < retries:
                time.sleep(2**attempt)
        logger.error("git push exhausted retries; commit kept locally")
        return False

    @staticmethod
    def _git(cmd: list[str], cwd: str):
        import subprocess
        return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
```
NOTE: keep the module-level `import subprocess` (used by the patched tests via `digest.agents.publisher.subprocess.run`); the `_git` helper must call `subprocess.run` resolved from the module namespace, so DO NOT shadow it with a local import — instead remove the inner `import subprocess` and rely on the top-level import. Corrected `_git`:
```python
    @staticmethod
    def _git(cmd: list[str], cwd: str):
        return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
```

- [ ] **Step 4: Run → pass** (4 passed). **Step 5: Commit** `feat: Publisher git commit/push (tolerant)`.

---

## Task 4: Hugo site scaffold (minimal, no external theme)

**Files:** Create `site/hugo.toml`, `site/content/posts/.gitkeep`, `site/i18n/en.toml`, `site/i18n/vi.toml`, `site/layouts/_default/baseof.html`, `site/layouts/_default/single.html`, `site/layouts/_default/list.html`, `site/layouts/index.html`

- [ ] **Step 1: `site/hugo.toml`**
```toml
baseURL = "https://example.github.io/ai-digest/"
title = "AI Digest"
defaultContentLanguage = "en"
defaultContentLanguageInSubdir = true

[languages.en]
languageName = "English"
weight = 1
[languages.en.params]
description = "Daily AI & tech digest"

[languages.vi]
languageName = "Tiếng Việt"
weight = 2
[languages.vi.params]
description = "Bản tin AI & công nghệ hằng ngày"

[taxonomies]
category = "categories"
tag = "tags"
```
(`baseURL` is a placeholder; the real value is set in the setup checklist / via the CI `--baseURL` flag.)

- [ ] **Step 2: `site/content/posts/.gitkeep`** — empty file (keeps the dir in git).

- [ ] **Step 3: i18n strings** `site/i18n/en.toml`:
```toml
[readMore]
other = "Read more"
[sources]
other = "Sources"
```
`site/i18n/vi.toml`:
```toml
[readMore]
other = "Đọc tiếp"
[sources]
other = "Nguồn"
```

- [ ] **Step 4: `site/layouts/_default/baseof.html`**
```html
<!DOCTYPE html>
<html lang="{{ .Site.Language.Lang }}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{{ if .Title }}{{ .Title }} · {{ end }}{{ .Site.Title }}</title>
</head>
<body>
  <header>
    <a href="{{ "/" | relLangURL }}">{{ .Site.Title }}</a>
    {{ range .Site.Languages }}
      <a href="{{ printf "/%s/" .Lang | relURL }}">{{ .LanguageName }}</a>
    {{ end }}
  </header>
  <main>{{ block "main" . }}{{ end }}</main>
</body>
</html>
```

- [ ] **Step 5: `site/layouts/index.html`** (homepage grouped by day)
```html
{{ define "main" }}
  <h1>{{ .Site.Title }}</h1>
  {{ range .Pages.GroupByDate "2006-01-02" }}
    <section>
      <h2>{{ .Key }}</h2>
      <ul>
        {{ range .Pages }}
          <li>
            <a href="{{ .RelPermalink }}">{{ .Title }}</a>
            {{ with .Params.category }}<em>[{{ . }}]</em>{{ end }}
            <p>{{ .Summary }}</p>
          </li>
        {{ end }}
      </ul>
    </section>
  {{ end }}
{{ end }}
```

- [ ] **Step 6: `site/layouts/_default/single.html`** (post detail)
```html
{{ define "main" }}
  <article>
    <h1>{{ .Title }}</h1>
    <p><time>{{ .Date.Format "2006-01-02" }}</time>
       {{ with .Params.category }} · {{ . }}{{ end }}</p>
    {{ .Content }}
    {{ with .Params.tags }}
      <p>{{ range . }}<span>#{{ . }}</span> {{ end }}</p>
    {{ end }}
  </article>
{{ end }}
```

- [ ] **Step 7: `site/layouts/_default/list.html`** (category/tag/section lists)
```html
{{ define "main" }}
  <h1>{{ .Title }}</h1>
  <ul>
    {{ range .Pages }}
      <li><a href="{{ .RelPermalink }}">{{ .Title }}</a> — <time>{{ .Date.Format "2006-01-02" }}</time></li>
    {{ end }}
  </ul>
{{ end }}
```

- [ ] **Step 8: Commit** `feat: minimal Hugo site (i18n EN/VI, homepage by day, taxonomy)`.

---

## Task 5: GitHub Actions deploy workflow

**Files:** Create `.github/workflows/deploy.yml`

- [ ] **Step 1: Write the workflow**
```yaml
name: Deploy site to GitHub Pages

on:
  push:
    branches: [main, master]
    paths: ["site/**", ".github/workflows/deploy.yml"]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: pages
  cancel-in-progress: true

jobs:
  build:
    runs-on: ubuntu-latest
    env:
      HUGO_VERSION: 0.140.2
    steps:
      - uses: actions/checkout@v4
        with:
          submodules: recursive
      - name: Install Hugo
        run: |
          wget -O hugo.deb https://github.com/gohugoio/hugo/releases/download/v${HUGO_VERSION}/hugo_extended_${HUGO_VERSION}_linux-amd64.deb
          sudo dpkg -i hugo.deb
      - name: Configure Pages
        id: pages
        uses: actions/configure-pages@v5
      - name: Build
        run: hugo --minify --source site --baseURL "${{ steps.pages.outputs.base_url }}/"
      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: site/public

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

- [ ] **Step 2: Commit** `ci: deploy Hugo site to GitHub Pages on push`.

---

## Task 6: Install Hugo locally and verify the site builds

**Files:** none (verification only; may add a throwaway sample post and delete it)

- [ ] **Step 1: Install Hugo extended to ~/.local/bin (no sudo)**
```bash
cd /tmp
HUGO_VERSION=0.140.2
wget -q -O hugo.tar.gz https://github.com/gohugoio/hugo/releases/download/v${HUGO_VERSION}/hugo_extended_${HUGO_VERSION}_linux-amd64.tar.gz
tar -xzf hugo.tar.gz hugo
mkdir -p ~/.local/bin && mv hugo ~/.local/bin/hugo
export PATH="$HOME/.local/bin:$PATH"
hugo version
```
If the download is blocked by the sandbox network, mark this step BLOCKED and report it (CI still installs Hugo, so the site will build in CI regardless) — do NOT spend long retrying.

- [ ] **Step 2: Create a sample post via the Python Publisher and build**
```bash
cd /home/dungnd/Desktop/Workspace/ai-digest && export PATH="$HOME/.local/bin:$PATH"
uv run python -c "
from digest.agents.publisher import Publisher
from digest.core.content_types import BlogPost
p = BlogPost(lang='en', title='Hello AI', slug='hello-ai', date='2026-06-16',
             category='Tools', tags=('ai',), summary='Sample.', body='# Hi\n\nBody.',
             sources=('https://a.com',))
pv = BlogPost(**{**p.__dict__, 'lang':'vi', 'title':'Xin chào AI'})
Publisher(site_dir='site').write_posts([p, pv])
print('sample posts written')
"
hugo --source site --baseURL "http://localhost/"
```
Expected: Hugo reports pages built with EN and VI, exit 0, output in `site/public/`.

- [ ] **Step 3: Clean up the sample + build output**
```bash
cd /home/dungnd/Desktop/Workspace/ai-digest
rm -f site/content/posts/2026-06-16-hello-ai.en.md site/content/posts/2026-06-16-hello-ai.vi.md
rm -rf site/public site/resources
```
Add `site/public/` and `site/resources/` to `.gitignore`:
```
site/public/
site/resources/
```

- [ ] **Step 4: Commit** `chore: gitignore Hugo build output` (only the .gitignore change; no sample posts committed).

---

## Task 7: Full suite check
- [ ] Run `uv run pytest -v`. Expect green (cumulative + render 3 + publisher 7). Report the number.

## Done criteria for Milestone 5
- `render_post`/`post_filename`, `Publisher` (write + tolerant git) implemented + tested.
- Hugo site builds locally (or BLOCKED only by sandbox network, with CI as fallback) producing EN + VI output, homepage grouped by day, working category/tag pages.
- `.github/workflows/deploy.yml` present and valid.
- `uv run pytest` green; all committed.

**Next:** Milestone 6 (Telegram) — Reporter, Approver, post state machine, and the two entrypoints (`orchestrator.py`, `approver.py`) that wire the whole pipeline together.
