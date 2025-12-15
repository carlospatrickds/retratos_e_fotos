import streamlit as st
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
import io
import math
#==============================

#Configurações iniciais

#==============================

st.set_page_config(page_title="Fotos 10x15 em A4", layout="wide") st.title("📸 Montagem de Fotos para Impressão (A4)")

DPI = 300  # resolução para gráfica A4_WIDTH_MM, A4_HEIGHT_MM = 210, 297

#==============================

#Funções auxiliares

#==============================

def mm_to_px(mm, dpi=DPI): return int(mm * dpi / 25.4)

def resize_crop(image, target_w_px, target_h_px): """Redimensiona e corta para preencher exatamente o tamanho""" img_ratio = image.width / image.height target_ratio = target_w_px / target_h_px

if img_ratio > target_ratio:
    new_height = target_h_px
    new_width = int(new_height * img_ratio)
else:
    new_width = target_w_px
    new_height = int(new_width / img_ratio)

image = image.resize((new_width, new_height), Image.LANCZOS)

left = (new_width - target_w_px) // 2
top = (new_height - target_h_px) // 2
return image.crop((left, top, left + target_w_px, top + target_h_px))

def gerar_a4(imagens, layout): a4_px = Image.new( "RGB", (mm_to_px(A4_WIDTH_MM), mm_to_px(A4_HEIGHT_MM)), "white", )

for img, (x_mm, y_mm, w_mm, h_mm) in zip(imagens, layout):
    w_px = mm_to_px(w_mm)
    h_px = mm_to_px(h_mm)
    img = resize_crop(img, w_px, h_px)
    a4_px.paste(img, (mm_to_px(x_mm), mm_to_px(y_mm)))

return a4_px

def exportar_pdf(img_a4): buffer = io.BytesIO() c = canvas.Canvas(buffer, pagesize=A4)

img_buffer = io.BytesIO()
img_a4.save(img_buffer, format="JPEG", dpi=(DPI, DPI), quality=95)
img_buffer.seek(0)

c.drawImage(
    ImageReader(img_buffer),
    0,
    0,
    width=A4_WIDTH_MM * mm,
    height=A4_HEIGHT_MM * mm,
)
c.showPage()
c.save()

buffer.seek(0)
return buffer

#==============================

#Interface

#==============================

st.subheader("1️⃣ Envie as fotos") files = st.file_uploader( "Selecione as imagens", type=["jpg", "jpeg", "png"], accept_multiple_files=True, )

st.subheader("2️⃣ Escolha o layout") layout_tipo = st.selectbox( "Formato da folha A4", [ "10x15 (6 fotos por A4)", "10x15 + 5x7 (combinado)", ], )

if files: imagens = [Image.open(f).convert("RGB") for f in files]

if layout_tipo == "10x15 (6 fotos por A4)":
    layout = [
        (10, 10, 100, 150), (110, 10, 100, 150),
        (10, 160, 100, 150), (110, 160, 100, 150),
        (10, 310, 100, 150), (110, 310, 100, 150),
    ]
else:
    layout = [
        (10, 10, 100, 150), (110, 10, 100, 150),
        (10, 160, 50, 70), (70, 160, 50, 70),
        (130, 160, 50, 70), (10, 240, 50, 70),
    ]

total_por_folha = len(layout)
total_folhas = math.ceil(len(imagens) / total_por_folha)

st.info(f"Serão geradas {total_folhas} folha(s) A4")

if st.button("🔍 Gerar pré-visualização"):
    folhas = []
    for i in range(total_folhas):
        bloco = imagens[i * total_por_folha:(i + 1) * total_por_folha]
        folha = gerar_a4(bloco, layout[: len(bloco)])
        folhas.append(folha)

        st.image(folha, caption=f"Prévia A4 – Página {i+1}")

    st.subheader("3️⃣ Download")

    for idx, folha in enumerate(folhas):
        buf_jpg = io.BytesIO()
        folha.save(buf_jpg, format="JPEG", dpi=(DPI, DPI), quality=95)
        buf_jpg.seek(0)

        st.download_button(
            label=f"📥 Baixar JPEG – Página {idx+1}",
            data=buf_jpg,
            file_name=f"a4_fotos_{idx+1}.jpg",
            mime="image/jpeg",
        )

    st.success("Arquivos prontos para impressão em papel fotográfico (300 DPI)")
