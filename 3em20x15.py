import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io

st.set_page_config(page_title="Mosaico Tríptico", layout="centered")

st.title("🖼️ Criador de Mosaico Tríptico")
st.write("Envie 3 fotos, ajuste bordas e texto, e gere seu mosaico (20x15 cm).")

# --- Upload das 3 imagens ---
uploaded_files = st.file_uploader(
    "Arraste ou selecione **3 fotos** do seu celular",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True
)

# --- Parâmetros de personalização ---
col1, col2 = st.columns(2)
with col1:
    add_borders = st.checkbox("Adicionar bordas brancas", value=True)
    spacing = st.slider("Espaçamento entre fotos (px)", 0, 50, 10)
with col2:
    title = st.text_input("Título (opcional)", "Maragogi 2025")
    footer = st.text_input("Rodapé (opcional)", "")

generate_btn = st.button("✨ Gerar Mosaico")

if generate_btn:
    if len(uploaded_files) != 3:
        st.error("Por favor, envie **exatamente 3 fotos**.")
    else:
        # --- Abrir e redimensionar imagens ---
        images = [Image.open(file).convert("RGB") for file in uploaded_files]

        # Dimensões finais (20x15 cm) em pixels, assumindo 300 DPI (alta qualidade)
        cm_to_px = lambda cm: int(cm / 2.54 * 300)
        width_final = cm_to_px(20)
        height_final = cm_to_px(15)
        single_width = (width_final - 2 * spacing) // 3
        single_height = height_final

        resized = [img.resize((single_width, single_height)) for img in images]

        # --- Criar imagem final ---
        total_width = width_final + (20 if add_borders else 0)
        total_height = height_final + (80 if title or footer else 0) + (20 if add_borders else 0)
        final_img = Image.new("RGB", (total_width, total_height), "white" if add_borders else "black")

        # --- Montar mosaico ---
        start_x = (final_img.width - width_final) // 2
        start_y = (final_img.height - height_final) // 2
        x_offset = start_x
        for img in resized:
            final_img.paste(img, (x_offset, start_y))
            x_offset += single_width + spacing

        # --- Adicionar texto ---
        draw = ImageDraw.Draw(final_img)
        try:
            font = ImageFont.truetype("arial.ttf", 60)
        except:
            font = ImageFont.load_default()

        if title:
            draw.text((final_img.width // 2, 30), title, fill="black", anchor="mm", font=font)
        if footer:
            draw.text((final_img.width // 2, final_img.height - 30), footer, fill="black", anchor="mm", font=font)

        # --- Exibir e permitir download ---
        st.image(final_img, caption="Pré-visualização do Mosaico", use_container_width=True)

        buf = io.BytesIO()
        final_img.save(buf, format="JPEG", quality=95)
        buf.seek(0)
        st.download_button(
            label="📥 Baixar Mosaico",
            data=buf,
            file_name="mosaico_tripico.jpg",
            mime="image/jpeg"
        )