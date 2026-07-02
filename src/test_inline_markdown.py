import unittest

from inline_markdown import (
    extract_markdown_images,
    extract_markdown_links,
    split_nodes_delimiter,
    split_nodes_image,
    split_nodes_link,
    text_to_textnodes,
)
from textnode import TextNode, TextType


class TestSplitNodesDelimiter(unittest.TestCase):
    def test_code(self):
        node = TextNode("This is text with a `code block` word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(
            new_nodes,
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("code block", TextType.CODE),
                TextNode(" word", TextType.TEXT),
            ],
        )

    def test_bold(self):
        node = TextNode("This is text with a **bolded phrase** in the middle", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertEqual(
            new_nodes,
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("bolded phrase", TextType.BOLD),
                TextNode(" in the middle", TextType.TEXT),
            ],
        )

    def test_italic(self):
        node = TextNode("An _italic_ word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "_", TextType.ITALIC)
        self.assertEqual(
            new_nodes,
            [
                TextNode("An ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" word", TextType.TEXT),
            ],
        )

    def test_multiple_delimited_sections(self):
        node = TextNode("**bold** and **more bold**", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertEqual(
            new_nodes,
            [
                TextNode("bold", TextType.BOLD),
                TextNode(" and ", TextType.TEXT),
                TextNode("more bold", TextType.BOLD),
            ],
        )

    def test_delimiter_at_start(self):
        node = TextNode("`code` at the start", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(
            new_nodes,
            [
                TextNode("code", TextType.CODE),
                TextNode(" at the start", TextType.TEXT),
            ],
        )

    def test_no_delimiter(self):
        node = TextNode("Plain text with no delimiters", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(new_nodes, [TextNode("Plain text with no delimiters", TextType.TEXT)])

    def test_non_text_node_passthrough(self):
        node = TextNode("already bold", TextType.BOLD)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(new_nodes, [TextNode("already bold", TextType.BOLD)])

    def test_multiple_input_nodes(self):
        nodes = [
            TextNode("A `code` node", TextType.TEXT),
            TextNode("bold node", TextType.BOLD),
            TextNode("Another `snippet` here", TextType.TEXT),
        ]
        new_nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
        self.assertEqual(
            new_nodes,
            [
                TextNode("A ", TextType.TEXT),
                TextNode("code", TextType.CODE),
                TextNode(" node", TextType.TEXT),
                TextNode("bold node", TextType.BOLD),
                TextNode("Another ", TextType.TEXT),
                TextNode("snippet", TextType.CODE),
                TextNode(" here", TextType.TEXT),
            ],
        )

    def test_unmatched_delimiter_raises(self):
        node = TextNode("This has an `unclosed code block", TextType.TEXT)
        with self.assertRaises(ValueError):
            split_nodes_delimiter([node], "`", TextType.CODE)


class TestExtractMarkdown(unittest.TestCase):
    def test_extract_markdown_images(self):
        matches = extract_markdown_images(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png")], matches)

    def test_extract_multiple_images(self):
        text = (
            "This is text with a ![rick roll](https://i.imgur.com/aKaOqIh.gif) "
            "and ![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)"
        )
        self.assertListEqual(
            [
                ("rick roll", "https://i.imgur.com/aKaOqIh.gif"),
                ("obi wan", "https://i.imgur.com/fJRm4Vk.jpeg"),
            ],
            extract_markdown_images(text),
        )

    def test_extract_markdown_links(self):
        text = (
            "This is text with a link [to boot dev](https://www.boot.dev) "
            "and [to youtube](https://www.youtube.com/@bootdotdev)"
        )
        self.assertListEqual(
            [
                ("to boot dev", "https://www.boot.dev"),
                ("to youtube", "https://www.youtube.com/@bootdotdev"),
            ],
            extract_markdown_links(text),
        )

    def test_extract_links_ignores_images(self):
        text = "An ![image](https://example.com/i.png) and a [link](https://example.com)"
        self.assertListEqual(
            [("link", "https://example.com")],
            extract_markdown_links(text),
        )

    def test_extract_images_ignores_links(self):
        text = "A [link](https://example.com) and an ![image](https://example.com/i.png)"
        self.assertListEqual(
            [("image", "https://example.com/i.png")],
            extract_markdown_images(text),
        )

    def test_extract_no_matches(self):
        self.assertListEqual([], extract_markdown_images("Just plain text"))
        self.assertListEqual([], extract_markdown_links("Just plain text"))

    def test_extract_empty_alt_and_anchor(self):
        self.assertListEqual(
            [("", "https://example.com/i.png")],
            extract_markdown_images("![](https://example.com/i.png)"),
        )
        self.assertListEqual(
            [("", "https://example.com")],
            extract_markdown_links("[](https://example.com)"),
        )


class TestSplitNodesImage(unittest.TestCase):
    def test_split_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode(
                    "second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"
                ),
            ],
            new_nodes,
        )

    def test_split_single_image(self):
        node = TextNode(
            "![image](https://i.imgur.com/zjjcJKZ.png)", TextType.TEXT
        )
        self.assertListEqual(
            [TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png")],
            split_nodes_image([node]),
        )

    def test_split_image_with_trailing_text(self):
        node = TextNode(
            "start ![image](https://i.imgur.com/zjjcJKZ.png) end", TextType.TEXT
        )
        self.assertListEqual(
            [
                TextNode("start ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" end", TextType.TEXT),
            ],
            split_nodes_image([node]),
        )

    def test_split_no_images(self):
        node = TextNode("Just plain text", TextType.TEXT)
        self.assertListEqual([node], split_nodes_image([node]))

    def test_split_image_non_text_passthrough(self):
        node = TextNode("already bold", TextType.BOLD)
        self.assertListEqual([node], split_nodes_image([node]))

    def test_split_image_multiple_nodes(self):
        nodes = [
            TextNode("![a](https://ex.com/a.png)", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
        ]
        self.assertListEqual(
            [
                TextNode("a", TextType.IMAGE, "https://ex.com/a.png"),
                TextNode("bold", TextType.BOLD),
            ],
            split_nodes_image(nodes),
        )


class TestSplitNodesLink(unittest.TestCase):
    def test_split_links(self):
        node = TextNode(
            "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)",
            TextType.TEXT,
        )
        self.assertListEqual(
            [
                TextNode("This is text with a link ", TextType.TEXT),
                TextNode("to boot dev", TextType.LINK, "https://www.boot.dev"),
                TextNode(" and ", TextType.TEXT),
                TextNode(
                    "to youtube", TextType.LINK, "https://www.youtube.com/@bootdotdev"
                ),
            ],
            split_nodes_link([node]),
        )

    def test_split_single_link(self):
        node = TextNode("[link](https://boot.dev)", TextType.TEXT)
        self.assertListEqual(
            [TextNode("link", TextType.LINK, "https://boot.dev")],
            split_nodes_link([node]),
        )

    def test_split_link_with_surrounding_text(self):
        node = TextNode("go [here](https://boot.dev) now", TextType.TEXT)
        self.assertListEqual(
            [
                TextNode("go ", TextType.TEXT),
                TextNode("here", TextType.LINK, "https://boot.dev"),
                TextNode(" now", TextType.TEXT),
            ],
            split_nodes_link([node]),
        )

    def test_split_no_links(self):
        node = TextNode("Just plain text", TextType.TEXT)
        self.assertListEqual([node], split_nodes_link([node]))

    def test_split_link_ignores_images(self):
        node = TextNode(
            "![img](https://ex.com/i.png) and [link](https://boot.dev)", TextType.TEXT
        )
        self.assertListEqual(
            [
                TextNode("![img](https://ex.com/i.png) and ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://boot.dev"),
            ],
            split_nodes_link([node]),
        )

    def test_split_link_non_text_passthrough(self):
        node = TextNode("already code", TextType.CODE)
        self.assertListEqual([node], split_nodes_link([node]))


class TestTextToTextNodes(unittest.TestCase):
    def test_all_types(self):
        text = "This is **text** with an _italic_ word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"
        self.assertListEqual(
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("text", TextType.BOLD),
                TextNode(" with an ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" word and a ", TextType.TEXT),
                TextNode("code block", TextType.CODE),
                TextNode(" and an ", TextType.TEXT),
                TextNode(
                    "obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"
                ),
                TextNode(" and a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://boot.dev"),
            ],
            text_to_textnodes(text),
        )

    def test_plain_text(self):
        self.assertListEqual(
            [TextNode("Just plain text", TextType.TEXT)],
            text_to_textnodes("Just plain text"),
        )

    def test_only_bold(self):
        self.assertListEqual(
            [TextNode("bold", TextType.BOLD)],
            text_to_textnodes("**bold**"),
        )

    def test_multiple_same_type(self):
        self.assertListEqual(
            [
                TextNode("a ", TextType.TEXT),
                TextNode("b", TextType.BOLD),
                TextNode(" c ", TextType.TEXT),
                TextNode("d", TextType.BOLD),
            ],
            text_to_textnodes("a **b** c **d**"),
        )


if __name__ == "__main__":
    unittest.main()
