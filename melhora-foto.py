import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io

# -------------------------------
# CONFIGURAÇÃO DA PÁGINA
# -------------------------------
st.set_page_config(
    page_title="Melhorador de Fotos",
    layout="wide"
)

st.title("🖼️ Melhorador de Qualidade de Imagens")
st.caption("Melhore fotos borradas com controles avançados (sem IA pesada)")

# -------------------------------
# FUNÇÕES DE PROCESSAMENTO
# -------------------------------

def ajustar_brilho_contraste(img, brilho=0, contraste=1.0):
    return cv2.convertScaleAbs(img, alpha=contraste, beta=brilho)

def reduzir_ruido(img, intensidade):
    if intensidade > 0:
        return cv2.fastNlMeansDenoisingColored(
            img, None, intensidade, intensidade, 7, 21
        )
    return img

def aplicar_nitidez(img, intensidade):
    if intensidade <= 0:
        return img

    kernel = np.array([
        [0, -1, 0],
        [-1, 5 + intensidade, -1],
        [0, -1, 0]
    ])
    return cv2.filter2D(img, -1, kernel)

def aplicar_upscale(img, escala):
    if escala == 1:
        return img
    altura, largura = img.shape[:2]
    return cv2.resize(
        img,
        (largura * escala, altura * escala),
        interpolation=cv2.INTER_CUBIC
    )

def processar_imagem(img, brilho, contraste, ruido, nitidez, upscale):
    img = ajustar_brilho_contraste(img, brilho, contraste)
    img = reduzir_ruido(img, ruido)
    img = aplicar_nitidez(img, nitidez)
    img = aplicar_upscale(img, upscale)
    return img

# -------------------------------
# SIDEBAR – CONTROLES
# -------------------------------
st.sidebar.header("🎛️ Ajustes")

brilho = st.sidebar.slider("Brilho", -100, 100, 0)
contraste = st.sidebar.slider("Contraste", 0.5, 3.0, 1.2, 0.1)
ruido = st.sidebar.slider("Redução de Ruído", 0, 30, 5)
nitidez = st.sidebar.slider("Nitidez", 0, 3, 1)
upscale = st.sidebar.selectbox("Upscale (resolução)", [1, 2, 3])

# -------------------------------
# UPLOAD DA IMAGEM
# -------------------------------
uploaded_file = st.file_uploader(
    "📤 Envie uma imagem (JPG ou PNG)",
    type=["jpg", "jpeg", "png"]
)

if uploaded_file:
    try:
        # Leitura segura
        image = Image.open(uploaded_file).convert("RGB")
        img_np = np.array(image)
        img_cv = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)

        # Processamento
        img_processada = processar_imagem(
            img_cv,
            brilho,
            contraste,
            ruido,
            nitidez,
            upscale
        )

        img_final = cv2.cvtColor(img_processada, cv2.COLOR_BGR2RGB)

        # -------------------------------
        # EXIBIÇÃO
        # -------------------------------
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📸 Original")
            st.image(image, use_column_width=True)

        with col2:
            st.subheader("✨ Melhorada")
            st.image(img_final, use_column_width=True)

        # -------------------------------
        # DOWNLOAD
        # -------------------------------
        buffer = io.BytesIO()
        Image.fromarray(img_final).save(buffer, format="PNG")
        buffer.seek(0)

        st.download_button(
            label="⬇️ Baixar imagem melhorada",
            data=buffer,
            file_name="imagem_melhorada.png",
            mime="image/png"
        )

    except Exception as e:
        st.error("Erro ao processar a imagem.")
        st.exception(e)

else:
    st.info("Envie uma imagem para começar.")
