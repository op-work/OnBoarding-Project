def clean_html(html_str: str) -> str:
    """Strips all leading/trailing whitespace from each line in an HTML string to prevent Streamlit from creating Markdown code blocks."""
    if not html_str:
        return ""
    return "".join(line.strip() for line in html_str.splitlines())
