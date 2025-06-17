import markdownify


def html_to_md(html_content):
    """
    Convert HTML content to Markdown format.
    """
    md_content = markdownify.markdownify(
        html_content,
        heading_style="ATX",
    )
    return md_content