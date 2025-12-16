import streamlit as st
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import tempfile
import os

# =============================
# Configuração da página
# =============================
st.set_page_config(
    page_title="Fotos 10x15 em A4",
    layout="wide"
)

st.title("📸 Montagem de Fotos 10×15 em Folha A4")

st.write(
    "Envie suas fotos e o sistema irá montar automaticamente "
    "**4 fotos 10×15 por folha A4**, com pré-visualização e PDF pronto para impressão."
)

# =============================
# Upload das imagens
# =============================
uploaded_files = st.file_uploader(
    "Selecione as fotos",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True
)

if not uploaded_files:
    st.info("📂 Envie ao menos uma foto para começar.")
    st.stop()

# =============================
# Constantes
# =============================
DPI = 300

A4_WIDTH_CM = 21
A4_HEIGHT_CM = 29.7

PHOTO_WIDTH_CM = 10
PHOTO_HEIGHT_CM = 15

def cm_to_px(cm):
    return int((cm / 2.54) * DPI)

A4_WIDTH_PX = cm_to_px(A4_WIDTH_CM)
A4_HEIGHT_PX = cm_to_px(A4_HEIGHT_CM)

PHOTO_W_PX = cm_to_px(PHOTO_WIDTH_CM)
PHOTO_H_PX = cm_to_px(PHOTO_HEIGHT_CM)

# =============================
# Processamento das imagens
# =============================
processed_images = []

for file in uploaded_files:
    img = Image.open(file).convert("RGB")
    img = img.resize((PHOTO_W_PX, PHOTO_H_PX), Image.LANCZOS)
    processed_images.append(img)

# =============================
# Criar páginas A4 (4 fotos por página)
# =============================
pages = []

for i in range(0, len(processed_images), 4):
    page = Image.new("RGB", (A4_WIDTH_PX, A4_HEIGHT_PX), "white")
    batch = processed_images[i:i + 4]

    positions = [
        (0, 0),
        (PHOTO_W_PX, 0),
        (0, PHOTO_H_PX),
        (PHOTO_W_PX, PHOTO_H_PX)
    ]

    offset_x = (A4_WIDTH_PX - (PHOTO_W_PX * 2)) // 2
    offset_y = (A4_HEIGHT_PX - (PHOTO_H_PX * 2)) // 2

    for img, pos in zip(batch, positions):
        page.paste(img, (pos[0] + offset_x, pos[1] + offset_y))

    pages.append(page)

# =============================
# Pré-visualização
# =============================
st.subheader("👀 Pré-visualização")

for idx, page in enumerate(pages, start=1):
    st.markdown(f"**Página {idx}**")
    st.image(page, use_container_width=True)

# =============================
# Gerar PDF
# =============================
if st.button("📄 Gerar PDF para impressão"):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
        pdf_path = tmp_pdf.name

    c = canvas.Canvas(pdf_path, pagesize=A4)

    for page in pages:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_img:
            img_path = tmp_img.name
            page.save(img_path, "JPEG", quality=100)

        c.drawImage(
            img_path,
            0,
            0,
            width=A4[0],
            height=A4[1]
        )

        c.showPage()
        os.remove(img_path)

    c.save()

    with open(pdf_path, "rb") as f:
        st.download_button(
            label="⬇️ Baixar PDF",
            data=f,
            file_name="fotos_10x15_A4.pdf",
            mime="application/pdf"
        )

    os.remove(pdf_path)
