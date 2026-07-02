import unittest

from block_markdown import (
    BlockType,
    block_to_block_type,
    extract_title,
    markdown_to_blocks,
    markdown_to_html_node,
)


class TestMarkdownToBlocks(unittest.TestCase):
    def test_markdown_to_blocks(self):
        md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )

    def test_single_block(self):
        self.assertEqual(
            markdown_to_blocks("Just one paragraph"),
            ["Just one paragraph"],
        )

    def test_excessive_newlines(self):
        md = "First block\n\n\n\nSecond block"
        self.assertEqual(
            markdown_to_blocks(md),
            ["First block", "Second block"],
        )

    def test_leading_and_trailing_whitespace(self):
        md = "   \n\n  Block with spaces  \n\n   "
        self.assertEqual(
            markdown_to_blocks(md),
            ["Block with spaces"],
        )

    def test_empty_string(self):
        self.assertEqual(markdown_to_blocks(""), [])

    def test_heading_paragraph_list(self):
        md = """# This is a heading

This is a paragraph of text. It has some **bold** and _italic_ words inside of it.

- This is the first list item in a list block
- This is a list item
- This is another list item"""
        self.assertEqual(
            markdown_to_blocks(md),
            [
                "# This is a heading",
                "This is a paragraph of text. It has some **bold** and _italic_ words inside of it.",
                "- This is the first list item in a list block\n- This is a list item\n- This is another list item",
            ],
        )


class TestBlockToBlockType(unittest.TestCase):
    def test_heading(self):
        self.assertEqual(block_to_block_type("# Heading"), BlockType.HEADING)
        self.assertEqual(block_to_block_type("###### Heading"), BlockType.HEADING)

    def test_heading_requires_space(self):
        self.assertEqual(block_to_block_type("#Heading"), BlockType.PARAGRAPH)

    def test_heading_too_many_hashes(self):
        self.assertEqual(block_to_block_type("####### Heading"), BlockType.PARAGRAPH)

    def test_code(self):
        self.assertEqual(
            block_to_block_type("```\ncode here\n```"), BlockType.CODE
        )

    def test_code_inline_not_code_block(self):
        self.assertEqual(block_to_block_type("`code`"), BlockType.PARAGRAPH)

    def test_quote(self):
        self.assertEqual(block_to_block_type("> a quote"), BlockType.QUOTE)
        self.assertEqual(
            block_to_block_type("> line one\n> line two"), BlockType.QUOTE
        )

    def test_quote_no_space_allowed(self):
        self.assertEqual(block_to_block_type(">quote"), BlockType.QUOTE)

    def test_quote_broken_line(self):
        self.assertEqual(
            block_to_block_type("> line one\nline two"), BlockType.PARAGRAPH
        )

    def test_unordered_list(self):
        self.assertEqual(
            block_to_block_type("- item one\n- item two"), BlockType.UNORDERED_LIST
        )

    def test_unordered_list_requires_space(self):
        self.assertEqual(block_to_block_type("-item"), BlockType.PARAGRAPH)

    def test_ordered_list(self):
        self.assertEqual(
            block_to_block_type("1. first\n2. second\n3. third"),
            BlockType.ORDERED_LIST,
        )

    def test_ordered_list_wrong_start(self):
        self.assertEqual(
            block_to_block_type("2. first\n3. second"), BlockType.PARAGRAPH
        )

    def test_ordered_list_wrong_increment(self):
        self.assertEqual(
            block_to_block_type("1. first\n3. second"), BlockType.PARAGRAPH
        )

    def test_paragraph(self):
        self.assertEqual(
            block_to_block_type("Just a normal paragraph of text."),
            BlockType.PARAGRAPH,
        )

    def test_paragraph_multiline(self):
        self.assertEqual(
            block_to_block_type("Line one\nLine two"), BlockType.PARAGRAPH
        )


class TestMarkdownToHTMLNode(unittest.TestCase):
    def test_paragraphs(self):
        md = """
This is **bolded** paragraph
text in a p
tag here

This is another paragraph with _italic_ text and `code` here

"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p><p>This is another paragraph with <i>italic</i> text and <code>code</code> here</p></div>",
        )

    def test_codeblock(self):
        md = """
```
This is text that _should_ remain
the **same** even with inline stuff
```
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><pre><code>This is text that _should_ remain\nthe **same** even with inline stuff\n</code></pre></div>",
        )

    def test_headings(self):
        md = """
# Heading one

### Heading three with **bold**
"""
        node = markdown_to_html_node(md)
        self.assertEqual(
            node.to_html(),
            "<div><h1>Heading one</h1><h3>Heading three with <b>bold</b></h3></div>",
        )

    def test_quote(self):
        md = """
> This is a quote
> with _italic_ text
"""
        node = markdown_to_html_node(md)
        self.assertEqual(
            node.to_html(),
            "<div><blockquote>This is a quote with <i>italic</i> text</blockquote></div>",
        )

    def test_unordered_list(self):
        md = """
- first **item**
- second item
- third `item`
"""
        node = markdown_to_html_node(md)
        self.assertEqual(
            node.to_html(),
            "<div><ul><li>first <b>item</b></li><li>second item</li><li>third <code>item</code></li></ul></div>",
        )

    def test_ordered_list(self):
        md = """
1. first item
2. second **item**
3. third item
"""
        node = markdown_to_html_node(md)
        self.assertEqual(
            node.to_html(),
            "<div><ol><li>first item</li><li>second <b>item</b></li><li>third item</li></ol></div>",
        )

    def test_mixed_document(self):
        md = """
# Title

A paragraph with a [link](https://boot.dev).

- one
- two
"""
        node = markdown_to_html_node(md)
        self.assertEqual(
            node.to_html(),
            '<div><h1>Title</h1><p>A paragraph with a <a href="https://boot.dev">link</a>.</p><ul><li>one</li><li>two</li></ul></div>',
        )


class TestExtractTitle(unittest.TestCase):
    def test_extract_title(self):
        self.assertEqual(extract_title("# Hello"), "Hello")

    def test_extract_title_strips_whitespace(self):
        self.assertEqual(extract_title("#   Padded title   "), "Padded title")

    def test_extract_title_from_document(self):
        md = "# Tolkien Fan Club\n\nSome text\n\n## A subheading"
        self.assertEqual(extract_title(md), "Tolkien Fan Club")

    def test_extract_title_ignores_lower_headings(self):
        md = "## Not this\n\n# The real title"
        self.assertEqual(extract_title(md), "The real title")

    def test_extract_title_no_h1_raises(self):
        with self.assertRaises(ValueError):
            extract_title("## Only an h2\n\nSome text")


if __name__ == "__main__":
    unittest.main()
