from app.core.og_preview_fetcher import extract_og_image


def test_extract_og_image_when_present():
    html = '<html><head><meta property="og:image" content="https://example.com/a.jpg"></head></html>'
    assert extract_og_image(html) == "https://example.com/a.jpg"


def test_extract_og_image_when_content_attr_comes_first():
    html = '<meta content="https://example.com/b.jpg" property="og:image">'
    assert extract_og_image(html) == "https://example.com/b.jpg"


def test_extract_og_image_when_missing():
    html = "<html><head><title>no og tag here</title></head></html>"
    assert extract_og_image(html) is None
