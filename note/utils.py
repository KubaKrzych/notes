import markdown
import bleach


def render_markdown_to_safe_html(markdown_text):
    html = markdown.markdown(markdown_text)

    allowed_tags = list(bleach.sanitizer.ALLOWED_TAGS) + [
        "p",
        "pre",
        "img",
        "h1",
        "h2",
        "h3",
        "h4",
        "blockquote",
        "hr",
        "code",
    ]
    safe_html = bleach.clean(
        html,
        tags=allowed_tags,
        attributes={
            "img": ["src", "alt", "title"],
            **bleach.sanitizer.ALLOWED_ATTRIBUTES,
        },
    )

    return safe_html
