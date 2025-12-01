import streamlit as st
import cv2
import numpy as np
from PIL import Image

st.title("Melhorar qualidade de foto")

uploaded_file = st.file_uploader("Envie uma foto", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file)
    image_np = np.array(image)

    # Converter para OpenCV (BGR)
    image_cv = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)

    # Aumentar nitidez
    kernel = np.array([[0, -1, 0],
                       [-1, 5, -1],
                       [0, -1, 0]])
    sharp = cv2.filter2D(image_cv, -1, kernel)

    # Voltar para RGB
    sharp_rgb = cv2.cvtColor(sharp, cv2.COLOR_BGR2RGB)

    st.subheader("Antes")
    st.image(image, use_column_width=True)

    st.subheader("Depois")
    st.image(sharp_rgb, use_column_width=True)
