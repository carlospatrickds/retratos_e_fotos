# app_foto_porta_retrato.py
# Streamlit app: "Foto Porta-Retrato"
# - Faz upload da foto
# - Gera imagem pronta para impressão 10x15 cm (300 DPI padrão)
# - Mostra e exporta a área útil 10x6 cm com simulação de recorte meia-lua (curvatura no topo)

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
    # Faz um 'cover' (preencher) do canvas 10x15 mantendo proporção e cortando o excesso
    return ImageOps.fit(img, target_size_px, method=Image.LANCZOS, centering=(0.5, 0.5))

def create_semicircle_mask_top(size):
    # size: (w, h)
    w, h = size
    mask = Image.new('L', (w, h), 255)  # comece branco (manter)
    draw = ImageDraw.Draw(mask)
    # desenha uma elipse grande por cima para recortar o topo (preencher com preto = remover)
    # bbox escolhido para garantir uma curva suave que corta a parte superior
    bbox = (-w, -h * 2, w * 2, h)
    draw.ellipse(bbox, fill=0)
    return mask

def apply_mask(image, mask, background=(255,255,255)):
    # image: RGB do tamanho do mask
    bg = Image.new('RGB', image.size, background)
    result = Image.composite(image, bg, mask)
    return result

# UI: configurações
uploaded = st.file_uploader("Faça upload da foto", type=["jpg","jpeg","png","webp","heic"], accept_multiple_files=False)
DPI = st.slider("Resolução para impressão (DPI)", min_value=150, max_value=600, value=300, step=50)
show_preview_mask = st.checkbox("Mostrar área 10×6 cm e simulação meia-lua", value=True)

if uploaded:
    # abre imagem
    try:
        img = Image.open(uploaded).convert('RGB')
    except Exception as e:
        st.error("Não foi possível abrir a imagem: {}".format(e))
        st.stop()

    st.subheader("Imagem original")
    st.image(img, use_column_width=True)

    # tamanhos em px
    w_print = cm_to_px(10, DPI)   # 10 cm largura
    h_print = cm_to_px(15, DPI)   # 15 cm altura
    w_final = cm_to_px(10, DPI)   # 10 cm largura para recorte
    h_final = cm_to_px(6, DPI)    # 6 cm altura para recorte

    # gera imagem 10x15 pronta para impressão (cover)
    print_img = make_print_image(img, (w_print, h_print))

    st.subheader("Preview 10×15 (pronto para impressão)")
    st.image(print_img, width=400)

    # Gera a área de 10x6 que será recortada depois (centralizada horizontalmente e posicionada verticalmente)
    # vamos posicionar a área recortada centralizada horizontal e com topo alinhado ao topo físico do papel (opção)
    # aqui vamos centralizar verticalmente na 10x15 para que você possa escolher o melhor enquadramento antes de imprimir

    # Calcula posição do recorte centralizado na folha 10x15
    crop_x = (w_print - w_final) // 2
    crop_y = (h_print - h_final) // 2
    crop_box = (crop_x, crop_y, crop_x + w_final, crop_y + h_final)
    crop_img = print_img.crop(crop_box)

    if show_preview_mask:
        st.subheader("Área 10×6 cm - com simulação de meia-lua (curva em cima)")
        # cria máscara e aplica para mostrar como ficará
        mask = create_semicircle_mask_top((w_final, h_final))
        preview = apply_mask(crop_img, mask)
        # redimensiona o preview pra exibição na tela sem perder proporção
        st.image(preview, width=400)

    # Botões para download
    st.subheader("Download")

    # Salva o print_img (10x15) em bytes
    buf1 = io.BytesIO()
    print_img.save(buf1, format='JPEG', quality=95, dpi=(DPI, DPI))
    buf1.seek(0)

    st.download_button(
        label="Baixar imagem 10×15 pronta (JPEG)",
        data=buf1,
        file_name="foto_10x15.jpg",
        mime="image/jpeg"
    )

    # Salva a área 10x6 com máscara aplicada (fundo branco onde cortado)
    mask = create_semicircle_mask_top((w_final, h_final))
    final_10x6 = apply_mask(crop_img, mask)
    buf2 = io.BytesIO()
    final_10x6.save(buf2, format='JPEG', quality=95, dpi=(DPI, DPI))
    buf2.seek(0)

    st.download_button(
        label="Baixar área 10×6 com meia-lua (JPEG)",
        data=buf2,
        file_name="foto_10x6_meialua.jpg",
        mime="image/jpeg"
    )

    st.markdown("---")
    st.info("Dica: imprima a imagem 10×15 e recorte a área 10×6 usando a referência visual. O arquivo 10×6 já tem a curva simulada no topo; caso precise de fundo transparente, altere o código para salvar PNG com canal alfa.")

    st.caption("Desenvolvido: Foto Porta-Retrato — use os ajustes caso queira mudar posicionamento do recorte (ex.: alinhar ao topo em vez de centralizar).")

else:
    st.info("Envie uma imagem acima para começar.")
