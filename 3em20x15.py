# app.py
"""
Streamlit app: Triptych collage for 20x15 cm prints.
Requirements: streamlit, pillow
Install:
    pip install streamlit pillow
Run:
    streamlit run app.py
"""

import io
from PIL import Image, ImageDraw, ImageFont, ImageOps
import streamlit as st
import math

st.set_page_config(page_title="Triptych 20x15 - Maragogi", layout="wide")

st.title("Montagem 3 fotos — 20 x 15 cm (paisagem)")

# Upload
st.sidebar.header("Imagens")
imgs = st.sidebar.file_uploader("Envie 3 fotos (um por vez ou multi):", type=["jpg","jpeg","png"], accept_multiple_files=True)
if imgs:
    files = imgs[:3]
else:
    files = []

# Options
st.sidebar.header("Configurações de saída")
dpi = st.sidebar.selectbox("Resolução (DPI)", [150, 200, 300, 600], index=2)
# target size in cm
width_cm = 20.0
height_cm = 15.0

# Convert cms and mm to pixels
def cm_to_px(cm, dpi):
    inches = cm / 2.54
    px = int(round(inches * dpi))
    return px

def mm_to_px(mm, dpi):
    inches = mm / 25.4
    return int(round(inches * dpi))

canvas_w = cm_to_px(width_cm, dpi)
canvas_h = cm_to_px(height_cm, dpi)

st.sidebar.markdown(f"**Tamanho final:** {width_cm} × {height_cm} cm → {canvas_w} × {canvas_h} px (@{dpi} dpi)")

st.sidebar.header("Layout")
border_mm = st.sidebar.slider("Borda externa (mm)", 0, 30, 10)
spacing_mm = st.sidebar.slider("Espaçamento entre fotos (mm)", 0, 20, 8)
apply_title = st.sidebar.checkbox("Adicionar título (topo)", value=True)
title_text = st.sidebar.text_input("Título", value="MARAGOGI 2025")
title_font_size_pt = st.sidebar.slider("Tamanho do título (pt)", 12, 80, 48)
apply_footer = st.sidebar.checkbox("Adicionar nota de rodapé (rodapé)", value=False)
footer_text = st.sidebar.text_input("Nota de rodapé", value="")
footer_font_size_pt = st.sidebar.slider("Tamanho do rodapé (pt)", 8, 36, 18)

# Convert mm settings to pixels
border_px = mm_to_px(border_mm, dpi)
spacing_px = mm_to_px(spacing_mm, dpi)

st.write("Arraste as imagens (até 3). As imagens serão ajustadas mantendo proporção.")

if len(files) < 1:
    st.info("Envie 3 imagens para habilitar a montagem.")
    st.stop()

# pad images list to 3 with None if fewer uploaded
while len(files) < 3:
    files.append(None)

# Load images (PIL)
pil_imgs = []
for f in files:
    if f is None:
        pil_imgs.append(None)
    else:
        img = Image.open(f).convert("RGBA")
        pil_imgs.append(img)

# Attempt to load a truetype font (DejaVu comes often with PIL). Fallback to default.
def load_font(pt, bold=False):
    try:
        if bold:
            return ImageFont.truetype("DejaVuSans-Bold.ttf", pt)
        else:
            return ImageFont.truetype("DejaVuSans.ttf", pt)
    except Exception:
        return ImageFont.load_default()

# Prepare blank canvas (white)
canvas = Image.new("RGB", (canvas_w, canvas_h), color=(255,255,255))
draw = ImageDraw.Draw(canvas)

# Reserve space for title and footer
top_margin = 0
bottom_margin = 0
if apply_title and title_text.strip() != "":
    # estimate title height using font
    font_title = load_font(title_font_size_pt, bold=True)
    bbox = draw.textbbox((0,0), title_text, font=font_title)
    title_h = bbox[3] - bbox[1]
    top_margin = int(title_h * 1.4)  # padding
else:
    font_title = None

if apply_footer and footer_text.strip() != "":
    font_footer = load_font(footer_font_size_pt, bold=False)
    bbox = draw.textbbox((0,0), footer_text, font=font_footer)
    footer_h = bbox[3] - bbox[1]
    bottom_margin = int(footer_h * 1.4)
else:
    font_footer = None

# Compute area available for the three images
inner_w = canvas_w - 2*border_px
inner_h = canvas_h - 2*border_px - top_margin - bottom_margin

# Deduct spacing (two gaps between three images)
inner_w_for_images = inner_w - 2*spacing_px
slot_w = int(inner_w_for_images / 3)
slot_h = inner_h

# Starting top-left point for first image
x0 = border_px
y0 = border_px + top_margin

# Helper to fit image into slot while keeping aspect ratio and centering (letterbox)
def fit_and_paste(base, img, slot_w, slot_h, x, y):
    if img is None:
        # draw a light gray placeholder rectangle
        placeholder = Image.new("RGB", (slot_w, slot_h), (245,245,245))
        base.paste(placeholder, (x,y))
        return
    # Resize preserving aspect ratio
    img_w, img_h = img.size
    # Determine scaling factor
    scale = min(slot_w / img_w, slot_h / img_h)
    new_w = max(1, int(round(img_w * scale)))
    new_h = max(1, int(round(img_h * scale)))
    img_resized = img.resize((new_w, new_h), resample=Image.LANCZOS)

    # create slot background (white)
    slot_bg = Image.new("RGBA", (slot_w, slot_h), (255,255,255,255))
    # paste centered
    paste_x = (slot_w - new_w) // 2
    paste_y = (slot_h - new_h) // 2
    slot_bg.paste(img_resized, (paste_x, paste_y), img_resized if img_resized.mode=="RGBA" else None)
    base.paste(slot_bg.convert("RGB"), (x,y))

# Paste three images
for i in range(3):
    xi = x0 + i*(slot_w + spacing_px)
    fit_and_paste(canvas, pil_imgs[i], slot_w, slot_h, xi, y0)

# Draw optional thin separators (same color as background; if you want inner borders different, adapt here)
# (not drawing extra inner border to keep clean white look - images already separated by spacing)

# Draw title
if apply_title and title_text.strip() != "":
    # center top
    text = title_text.strip()
    font = font_title or load_font(title_font_size_pt, bold=True)
    bbox = draw.textbbox((0,0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    tx = (canvas_w - text_w)//2
    ty = max(5, border_px//2)
    draw.text((tx, ty), text, font=font, fill=(0,0,0))

# Draw footer
if apply_footer and footer_text.strip() != "":
    text = footer_text.strip()
    font = font_footer or load_font(footer_font_size_pt)
    bbox = draw.textbbox((0,0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    tx = (canvas_w - text_w)//2
    ty = canvas_h - border_px - text_h - 5
    draw.text((tx, ty), text, font=font, fill=(0,0,0))

# Preview
st.subheader("Visualização (amostragem)")
st.image(canvas, use_column_width=True)

# Prepare download
buf = io.BytesIO()
canvas.save(buf, format="PNG")
buf.seek(0)

st.download_button(
    label="Baixar imagem (PNG)",
    data=buf,
    file_name="montagem_20x15.png",
    mime="image/png"
)

st.markdown("---")
st.markdown("**Como usar no laboratório digital / impressão:**")
st.markdown(
    f"- A imagem foi gerada com {dpi} dpi e tem {canvas_w}×{canvas_h} px — adequada para revelar **{width_cm}×{height_cm} cm**.\n"
    "- Se sua gráfica pede JPG em alta qualidade, converta o PNG para JPG em um editor (ou posso adicionar opção aqui)."
)

st.markdown("**Dicas:** se desejar borda mais larga para margem de corte aumente a Borda externa (mm).")