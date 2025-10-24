import streamlit as st
from PIL import Image, ImageDraw
import io

st.title("Porta-Retrato Meia Lua Simples")

uploaded_file = st.file_uploader("Escolha uma foto", type=['jpg', 'png', 'jpeg'])

if uploaded_file:
    image = Image.open(uploaded_file)
    
    # Dimensões fixas
    largura, altura = 600, 900  # 10x15cm em ~150 DPI
    
    # Redimensionar
    image = image.resize((largura, altura))
    
    # Criar máscara de meia-lua
    mascara = Image.new('L', (largura, altura), 0)
    draw = ImageDraw.Draw(mascara)
    draw.pieslice([150, 0, 450, 600], start=180, end=360, fill=255)
    
    # Aplicar máscara
    resultado = Image.new('RGB', (largura, altura), (0, 0, 0))
    resultado.paste(image, (0, 0), mascara)
    
    st.image(resultado, caption="Sua foto no formato meia-lua")
    
    # Download
    buf = io.BytesIO()
    resultado.save(buf, format='JPEG')
    st.download_button("Baixar imagem", buf.getvalue(), "porta_retrato.jpg", "image/jpeg")
