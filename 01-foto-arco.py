# app_foto_porta_retrato.py
# Streamlit app: "Foto Porta-Retrato"
# - Faz upload da foto
# - Gera imagem pronta para impressão 10x15 cm (300 DPI padrão)
# - Mostra e exporta a área útil 10x6 cm com simulação de recorte meia-lua no topo

import streamlit as st
from PIL import Image, ImageOps, ImageDraw
import io

st.set_page_config(page_title="Foto Porta-Retrato", layout="centered")
st.title("📸 Foto Porta-Retrato")
st.write("Envie uma foto; o app gera uma versão 10×15 cm pronta para imprimir e uma área 10×6 cm com simulação de meia-lua no topo.")

# Funções utilitárias
def cm_to_px(cm, dpi):
    return int(round(cm * dpi / 2.54))

def make_print_image(img, target_size_px):
    return ImageOps.fit(img, target_size_px, method=Image.LANCZOS, centering=(0.5, 0.5))

def create_semicircle_mask_top(size):
    w, h = size
    mask = Image.new('L', (w, h), 255)
    draw = ImageDraw.Draw(mask)
    bbox = (-w, -h * 2, w * 2, h)
    draw.ellipse(bbox, fill=0)
    return mask

def apply_mask(image, mask, background=(255,255,255)):
    bg = Image.new('RGB', image.size, background)
    result = Image.composite(image, bg, mask)
    return result

# UI: configurações
enquadramento = st.radio("Escolha o enquadramento:", ["Normal (A)", "Close (B)"], horizontal=True)
zoom_factor = 1.0 if enquadramento == "Normal (A)" else 1.3
uploaded = st.file_uploader("Faça upload da foto", type=["jpg","jpeg","png","webp","heic"], accept_multiple_files=False)
DPI = st.slider("Resolução para impressão (DPI)", min_value=150, max_value=600, value=300, step=50)
show_preview_mask = st.checkbox("Mostrar área 10×6 cm e simulação meia-lua", value=True)

if uploaded:
    try:
        img = Image.open(uploaded).convert('RGB')
    except Exception as e:
        st.error(f"Não foi possível abrir a imagem: {e}")
        st.stop()

    st.subheader("Imagem original")
    st.image(img, use_column_width=True)

    w_print = cm_to_px(10, DPI)
    h_print = cm_to_px(15, DPI)
    w_final = cm_to_px(10, DPI)
    h_final = cm_to_px(6, DPI)

    if zoom_factor != 1.0:
        new_w = int(img.width * zoom_factor)
        new_h = int(img.height * zoom_factor)
        img_zoom = img.resize((new_w, new_h), Image.LANCZOS)
    else:
        img_zoom = img

    print_img = make_print_image(img_zoom, (w_print, h_print))

    st.subheader("Preview 10×15 (pronto para impressão)")
    st.image(print_img, width=400)

    crop_x = (w_print - w_final) // 2
    crop_y = (h_print - h_final) // 2
    crop_box = (crop_x, crop_y, crop_x + w_final, crop_y + h_final)
    crop_img = print_img.crop(crop_box)

    if show_preview_mask:
        st.subheader("Área 10×6 cm - com simulação de meia-lua (curva em cima)")
        mask = create_semicircle_mask_top((w_final, h_final))
        preview = apply_mask(crop_img, mask)
        st.image(preview, width=400)

    st.subheader("Download")

    buf1 = io.BytesIO()
    print_img.save(buf1, format='JPEG', quality=95, dpi=(DPI, DPI))
    buf1.seek(0)
    st.download_button("Baixar imagem 10×15 pronta (JPEG)", buf1, "foto_10x15.jpg", "image/jpeg")

    mask = create_semicircle_mask_top((w_final, h_final))
    final_10x6 = apply_mask(crop_img, mask)
    buf2 = io.BytesIO()
    final_10x6.save(buf2, format='JPEG', quality=95, dpi=(DPI, DPI))
    buf2.seek(0)
    st.download_button("Baixar área 10×6 com meia-lua (JPEG)", buf2, "foto_10x6_meialua.jpg", "image/jpeg")

    st.markdown("---")
    st.info("Dica: imprima a imagem 10×15 e recorte a área 10×6 usando a referência visual.")
    st.caption("Desenvolvido: Foto Porta-Retrato")
else:
    st.info("Envie uma imagem acima para começar.")
