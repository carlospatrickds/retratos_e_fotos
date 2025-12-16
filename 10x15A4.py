import streamlit as st
from PIL import Image
import tempfile
import os

# =============================
# Configuração da página
# =============================
st.set_page_config(
    page_title="Fotos 10x15 em A4",
    layout="wide"
)

st.title("📸 Fotos 10×15 em A4")

st.write(
    "Envie suas fotos. O sistema monta automaticamente "
    "**4 fotos 10×15 por folha A4**, com pré-visualização e PDF pronto."
)

# =============================
# Upload
# =============================
files = st.file_uploader(
    "Selecione as fotos",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True
)

if not files:
    st.info("Envie ao menos uma imagem.")
    st.stop()

# =============================
# Constantes
# =============================
DPI = 300

def cm_to_px(cm):
    return int((cm / 2.54) * DPI)

A4_W, A4_H = cm_to_px(21), cm_to_px(29.7)
PHOTO_W, PHOTO_H = cm_to_px(10), cm_to_px(15)

# =============================
# Processar imagens
# =============================
photos = []

for f in files:
    img = Image.open(f).convert("RGB")
    img = img.resize((PHOTO_W, PHOTO_H), Image.LANCZOS)
    photos.append(img)

# =============================
# Criar páginas A4
# =============================
pages = []

for i in range(0, len(photos), 4):
    page = Image.new("RGB", (A4_W, A4_H), "white")
    batch = photos[i:i + 4]

    offset_x = (A4_W - (PHOTO_W * 2)) // 2
    offset_y = (A4_H - (PHOTO_H * 2)) // 2

    positions = [
        (0, 0),
        (PHOTO_W, 0),
        (0, PHOTO_H),
        (PHOTO_W, PHOTO_H)
    ]

    for img, (x, y) in zip(batch, positions):
        page.paste(img, (x + offset_x, y + offset_y))

    pages.append(page)

# =============================
# Pré-visualização
# =============================
st.subheader("👀 Pré-visualização")

for i, p in enumerate(pages, start=1):
    st.markdown(f"**Página {i}**")
    st.image(p, use_container_width=True)

# =============================
# Gerar PDF
# =============================
if st.button("📄 Gerar PDF"):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        pdf_path = tmp.name

    pages[0].save(
        pdf_path,
        save_all=True,
        append_images=pages[1:],
        resolution=DPI
    )

    with open(pdf_path, "rb") as f:
        st.download_button(
            "⬇️ Baixar PDF",
            data=f,
            file_name="fotos_10x15_A4.pdf",
            mime="application/pdf"
        )

    os.remove(pdf_path)
