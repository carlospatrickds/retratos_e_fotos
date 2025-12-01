import streamlit as st
import os
import replicate
from PIL import Image
import io

# =============================
# 1. PEGAR TOKEN DO STREAMLIT
# =============================
REPLICATE_API_TOKEN = st.secrets["REPLICATE_API_TOKEN"]
os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN

# =============================
# 2. INTERFACE
# =============================
st.title("Melhorar Foto com IA (Replicate)")
uploaded_file = st.file_uploader("Envie uma foto borrada", type=["jpg", "png", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Original", use_column_width=True)

    st.write("🔄 Processando com IA, aguarde...")

    # =============================
    # 3. CHAMADA AO MODELO DO REPLICATE
    # =============================
    output = replicate.run(
        "tencentarc/gfpgan:latest",
        input={
            "img": uploaded_file.getvalue()
        }
    )

    improved_url = output

    st.image(improved_url, caption="Foto Melhorada", use_column_width=True)
