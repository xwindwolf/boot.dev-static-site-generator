# Static Site Generator

A small static site generator written in Python. It reads Markdown files from
`content/`, converts them to HTML using an HTML template, and writes a complete
static website to `docs/` — copying over static assets (CSS, images) along the
way. (The site is output to `docs/` because GitHub Pages can serve directly from
that directory on the main branch.)

> This is a [Boot.dev](https://www.boot.dev) guided project, built as part of the
> [Build a Static Site Generator in Python](https://www.boot.dev/courses/build-static-site-generator-python)
> course.

## What it does

- Parses inline Markdown (bold, italic, code, links, images) into text nodes.
- Parses block-level Markdown (headings, paragraphs, quotes, code blocks,
  ordered and unordered lists) into an HTML node tree.
- Extracts the page title from the first `# ` heading.
- Injects the rendered content and title into `template.html` via the
  `{{ Content }}` and `{{ Title }}` placeholders.
- Recursively generates a page for every `.md` file under `content/`, mirroring
  the directory structure into `docs/`.
- Copies everything in `static/` into `docs/` before generating pages.
- Supports a configurable base path (passed as a CLI argument) so the site can
  be hosted under a subdirectory, e.g. GitHub Pages at `/repo-name/`.

## Project layout

```
content/        Markdown source pages
static/         Static assets (CSS, images) copied verbatim to docs/
docs/           Generated site output (served by GitHub Pages)
template.html   HTML template with {{ Title }} and {{ Content }} placeholders
src/            Source code
  htmlnode.py         HTMLNode / LeafNode / ParentNode
  textnode.py         TextNode + conversion to HTMLNode
  inline_markdown.py  Inline Markdown parsing (delimiters, links, images)
  block_markdown.py   Block parsing, markdown -> HTML, title extraction
  copy_static.py      Recursive static-asset copy
  main.py             Entry point: copy static + generate pages
  test_*.py           Unit tests
main.sh         Build the site (base path /) and serve it locally
build.sh        Build the site for production (GitHub Pages base path)
test.sh         Run the unit test suite
```

## Usage

Build the site and serve it at http://localhost:8888:

```bash
./main.sh
```

Build for production (GitHub Pages), applying the repo-name base path:

```bash
./build.sh
```

Run the tests:

```bash
./test.sh
```
