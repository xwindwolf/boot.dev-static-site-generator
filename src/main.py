import os
import sys

from block_markdown import extract_title, markdown_to_html_node
from copy_static import copy_directory

dir_path_static = "./static"
dir_path_docs = "./docs"


def generate_page(
    from_path: str, template_path: str, dest_path: str, basepath: str
) -> None:
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")

    with open(from_path) as f:
        markdown = f.read()
    with open(template_path) as f:
        template = f.read()

    content = markdown_to_html_node(markdown).to_html()
    title = extract_title(markdown)

    page = template.replace("{{ Title }}", title).replace("{{ Content }}", content)
    page = page.replace('href="/', f'href="{basepath}')
    page = page.replace('src="/', f'src="{basepath}')

    dest_dir = os.path.dirname(dest_path)
    if dest_dir != "":
        os.makedirs(dest_dir, exist_ok=True)
    with open(dest_path, "w") as f:
        f.write(page)


def generate_pages_recursive(
    dir_path_content: str, template_path: str, dest_dir_path: str, basepath: str
) -> None:
    for entry in os.listdir(dir_path_content):
        content_path = os.path.join(dir_path_content, entry)
        dest_path = os.path.join(dest_dir_path, entry)
        if os.path.isfile(content_path):
            if content_path.endswith(".md"):
                dest_path = dest_path[: -len(".md")] + ".html"
                generate_page(content_path, template_path, dest_path, basepath)
        else:
            generate_pages_recursive(content_path, template_path, dest_path, basepath)


def main():
    basepath = sys.argv[1] if len(sys.argv) > 1 else "/"

    print("Copying static files to docs directory...")
    copy_directory(dir_path_static, dir_path_docs)
    generate_pages_recursive("content", "template.html", "docs", basepath)


if __name__ == "__main__":
    main()
