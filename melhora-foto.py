import streamlit as st
from PIL import Image
import torch
import numpy as np
import io
from realesrgan import RealESRGAN

# ----------------------------------
# CONFIGURAÇÃO DA PÁGINA
# ----------------------------------
st.set_page_config(
    page_title="Melhoria de Fotos com IA",
    layout="centered"
)

st.title("🧠 Super-resolução de Fotos com IA")
st.caption("Reconstrói detalhes e melhora fotos borradas usando inteligência artificial")

# ----------------------------------
# INICIALIZAÇÃO DO MODELO
# ----------------------------------
@st.cache_resource
def carregar_modelo():
    device = torch.device("cpu")
    model = RealESRGAN(device, scale=2)
    model.load_weights("RealESRGAN_x2.pth", download=True)
    return model

modelo = carregar_modelo()

# ----------------------------------
# UPLOAD
# ----------------------------------
uploaded_file = st.file_uploader(
    "📷 Envie uma foto",
    type=["jpg", "jpeg", "png"]
)

if uploaded_file:
    img = Image.open(uploaded_file).convert("RGB")

    st.subheader("Original")
    st.image(img, use_column_width=True)

    if st.button("🚀 Melhorar com IA"):
        with st.spinner("Processando com IA (pode demorar alguns segundos)..."):
            img_np = np.array(img)

            output = modelo.predict(img_np)

            img_final = Image.fromarray(output)

        st.subheader("Melhorada com IA")
        st.image(img_final, use_column_width=True)

        # DOWNLOAD
        buffer = io.BytesIO()
        img_final.save(buffer, format="PNG")
        buffer.seek(0)

        st.download_button(
            "⬇️ Baixar imagem melhorada",
            data=buffer,
            file_name="foto_melhorada_IA.png",
            mime="image/png"
        )
else:
    st.info("Envie uma imagem para iniciar o processamento.")
