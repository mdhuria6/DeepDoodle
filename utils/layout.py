from PIL import Image
from .config import PANEL_SIZE, MARGIN

def get_grid_dims():
    return (PANEL_SIZE * 2 + MARGIN * 3, PANEL_SIZE * 2 + MARGIN * 3)

def get_horizontal_strip_dims(page_chunk):
    return (PANEL_SIZE * len(page_chunk) + MARGIN * (len(page_chunk) + 1), PANEL_SIZE + MARGIN * 2)

def get_vertical_strip_dims(page_chunk):
    return (PANEL_SIZE + MARGIN * 2, PANEL_SIZE * len(page_chunk) + MARGIN * (len(page_chunk) + 1))


def compose_grid_2x2(page, page_chunk):
    """Composes a 2x2 grid layout."""
    for j, panel_path in enumerate(page_chunk):
        panel_img = Image.open(panel_path)
        row, col = j // 2, j % 2
        x_offset = MARGIN + (col * (PANEL_SIZE + MARGIN))
        y_offset = MARGIN + (row * (PANEL_SIZE + MARGIN))
        page.paste(panel_img, (x_offset, y_offset))
    return page

def compose_horizontal_strip(page, page_chunk):
    """Composes a 4x1 horizontal strip layout."""
    for j, panel_path in enumerate(page_chunk):
        panel_img = Image.open(panel_path)
        x_offset = MARGIN + (j * (PANEL_SIZE + MARGIN))
        y_offset = MARGIN
        page.paste(panel_img, (x_offset, y_offset))
    return page

def compose_vertical_strip(page, page_chunk):
    """Composes a 1x4 vertical strip layout."""
    for j, panel_path in enumerate(page_chunk):
        panel_img = Image.open(panel_path)
        x_offset = MARGIN
        y_offset = MARGIN + (j * (PANEL_SIZE + MARGIN))
        page.paste(panel_img, (x_offset, y_offset))
    return page
    
def compose_feature_left(page, page_chunk):
    """Composes a layout with one large panel on the left."""
    panel1_img = Image.open(page_chunk[0]).resize((PANEL_SIZE, PANEL_SIZE * 2 + MARGIN))
    page.paste(panel1_img, (MARGIN, MARGIN))
    panel2_img = Image.open(page_chunk[1])
    page.paste(panel2_img, (PANEL_SIZE + 2 * MARGIN, MARGIN))
    panel3_img = Image.open(page_chunk[2])
    page.paste(panel3_img, (PANEL_SIZE + 2 * MARGIN, PANEL_SIZE + 2 * MARGIN))
    return page

def compose_mixed_2x2(page, page_chunk):
    """Composes a mixed-size 2x2 layout."""
    total_col_height = PANEL_SIZE * 2 + MARGIN
    small_h = int(total_col_height / 3)
    large_h = total_col_height - small_h - MARGIN
    panel1_img = Image.open(page_chunk[0]).resize((PANEL_SIZE, small_h))
    page.paste(panel1_img, (MARGIN, MARGIN))
    panel3_img = Image.open(page_chunk[2]).resize((PANEL_SIZE, large_h))
    page.paste(panel3_img, (MARGIN, MARGIN + small_h + MARGIN))
    panel2_img = Image.open(page_chunk[1]).resize((PANEL_SIZE, large_h))
    page.paste(panel2_img, (MARGIN + PANEL_SIZE + MARGIN, MARGIN))
    panel4_img = Image.open(page_chunk[3]).resize((PANEL_SIZE, small_h))
    page.paste(panel4_img, (MARGIN + PANEL_SIZE + MARGIN, MARGIN + large_h + MARGIN))
    return page
