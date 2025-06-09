def render_comic(images: list) -> dict:
    html = "<div class='comic-strip'>" + "".join(
        f"<img src='{img}' alt='panel {i}' style='margin:5px;' />"
        for i, img in enumerate(images)
    ) + "</div>"
    return {"output": html, "panels": images}