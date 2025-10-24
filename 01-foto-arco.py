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

# Meia-lua melhorada: curva mais alta e avançada (opção C)
def create_semicircle_mask_top(size):
    w, h = size
    mask = Image.new('L', (w, h), 255)
    draw = ImageDraw.Draw(mask)
    # Aumenta a altura da elipse para cortar mais cabelo
    ellipse_height = h * 2.6
    bbox = (-w, -ellipse_height + h * 0.25, w * 2, h)
    draw.ellipse(bbox, fill=0)
    return mask

def apply_mask(image, mask, background=(255, 255, 255)):
    bg = Image.new('RGB', image.size, background)
    result = Image.composite(image, bg, mask)
    return result

# UI: configurações
enquadramento = st.radio("Escolha o enquadramento:", ["Normal (A)", "Close (B)"], horizontal=True)
zoom_factor = 1.0 if enquadramento == "Normal (A)" else 1.3
uploaded = st.file_uploader("Faça upload da foto", type=["jpg","jpeg","png","webp","heic"], accept_multiple_files=False)
DPI = st.slider("Resolução para impressão (DPI)", min_value=150, max_value=600, value=300, step=50)
show_preview_mask = st.checkbox("Mostrar área 10×6 cm e simulação meia-lua", value=True)

# Controle de posição vertical da área de corte
st.subheader("Ajuste de Posição")
ajuste_vertical = st.slider(
    "Ajuste vertical da área de corte", 
    min_value=-100, 
    max_value=100, 
    value=0,
    help="Move a área de corte para cima (valores negativos) ou para baixo (valores positivos)"
)

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

    # Aplicar ajuste vertical
    crop_x = (w_print - w_final) // 2
    crop_y = (h_print - h_final) // 2 + ajuste_vertical
    # Garantir que não saia dos limites
    crop_y = max(0, min(crop_y, h_print - h_final))
    
    crop_box = (crop_x, crop_y, crop_x + w_final, crop_y + h_final)
    crop_img = print_img.crop(crop_box)

    if show_preview_mask:
        st.subheader("Área 10×6 cm - com simulação de meia-lua (curva em cima)")
        mask = create_semicircle_mask_top((w_final, h_final))
        preview = apply_mask(crop_img, mask)
        st.image(preview, width=400)
        
        # Mostrar também a área de corte na imagem 10x15
        st.subheader("Visualização da área de corte no 10×15")
        img_with_crop = print_img.copy()
        draw = ImageDraw.Draw(img_with_crop)
        # Desenhar retângulo da área de corte
        draw.rectangle(crop_box, outline="red", width=3)
        # Desenhar linha do topo da meia-lua
        draw.line([(crop_x, crop_y), (crop_x + w_final, crop_y)], fill="blue", width=2)
        st.image(img_with_crop, width=400, caption="Área vermelha = corte 10×6 cm | Linha azul = topo da meia-lua")

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
    st.info("""
    **Dicas de uso:**
    - Use o ajuste vertical para posicionar as cabeças corretamente abaixo da meia-lua
    - Valores negativos movem a área de corte para **cima** (mais espaço acima das cabeças)
    - Valores positivos movem a área de corte para **baixo** (corta mais as cabeças)
    - Imprima a imagem 10×15 e recorte a área 10×6 usando a referência visual
    """)
    st.caption("Desenvolvido: Foto Porta-Retrato")
else:
    st.info("""
    **Envie uma imagem acima para começar.**
    
    **Instruções:**
    1. Faça upload da foto
    2. Escolha o enquadramento (Normal ou Close)
    3. Ajuste a posição vertical se necessário
    4. Visualize o resultado
    5. Baixe os arquivos para impressão
    """)
