import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import os

def cm_to_pixels(cm, dpi=300):
    """Converte centímetros para pixels considerando DPI"""
    return int(cm * dpi / 2.54)

def create_10x15_pdf(image_path, output_path):
    """Cria um PDF A4 com a imagem no formato 10x15cm centralizada"""
    
    # DPI para alta qualidade de impressão
    dpi = 300
    
    # Tamanhos em pixels
    a4_width_px = cm_to_pixels(21, dpi)  # A4 width: 21cm
    a4_height_px = cm_to_pixels(29.7, dpi)  # A4 height: 29.7cm
    img_width_px = cm_to_pixels(15, dpi)  # 15cm em pixels
    img_height_px = cm_to_pixels(10, dpi)  # 10cm em pixels
    
    # Criar imagem A4 em branco
    a4_image = Image.new('RGB', (a4_width_px, a4_height_px), 'white')
    draw = ImageDraw.Draw(a4_image)
    
    # Carregar e redimensionar a imagem original
    original_image = Image.open(image_path)
    
    # Redimensionar mantendo a proporção para caber em 10x15cm
    resized_image = original_image.resize((img_width_px, img_height_px), Image.LANCZOS)
    
    # Calcular posição para centralizar
    x_pos = (a4_width_px - img_width_px) // 2
    y_pos = (a4_height_px - img_height_px) // 2
    
    # Colar a imagem redimensionada no A4
    a4_image.paste(resized_image, (x_pos, y_pos))
    
    # Adicionar guias de corte (linhas vermelhas)
    draw.line([(x_pos, y_pos), (x_pos + img_width_px, y_pos)], fill='red', width=3)
    draw.line([(x_pos, y_pos + img_height_px), (x_pos + img_width_px, y_pos + img_height_px)], fill='red', width=3)
    draw.line([(x_pos, y_pos), (x_pos, y_pos + img_height_px)], fill='red', width=3)
    draw.line([(x_pos + img_width_px, y_pos), (x_pos + img_width_px, y_pos + img_height_px)], fill='red', width=3)
    
    # Adicionar texto informativo
    try:
        # Tentar usar fonte padrão, se não conseguir, não adiciona texto
        font = ImageFont.load_default()
        draw.text((50, 50), "Imagem 10x15cm - Corte nas linhas vermelhas", fill='black', font=font)
    except:
        pass
    
    # Salvar como PDF
    a4_image.save(output_path, "PDF", resolution=dpi)
    return output_path

def main():
    st.set_page_config(
        page_title="Conversor 10x15cm para PDF",
        page_icon="🖼️",
        layout="centered"
    )
    
    st.title("🖼️ Conversor de Imagem para PDF 10x15cm")
    st.markdown("""
    Faça upload de uma imagem e converta para o formato 10cm x 15cm em PDF para impressão em papel cartão.
    
    **Instruções:**
    1. Faça upload da imagem
    2. A imagem será redimensionada para 10x15cm
    3. Baixe o PDF pronto para impressão em A4
    4. Corte seguindo as linhas vermelhas
    """)
    
    # Upload da imagem
    uploaded_file = st.file_uploader(
        "Escolha uma imagem", 
        type=['jpg', 'jpeg', 'png', 'bmp', 'tiff'],
        help="Formatos suportados: JPG, PNG, BMP, TIFF"
    )
    
    if uploaded_file is not None:
        # Mostrar preview da imagem
        image = Image.open(uploaded_file)
        st.image(image, caption="Imagem Original", use_column_width=True)
        
        # Informações da imagem
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Largura Original", f"{image.width}px")
        with col2:
            st.metric("Altura Original", f"{image.height}px")
        with col3:
            st.metric("Formato", uploaded_file.type.split('/')[-1].upper())
        
        # Opções de qualidade
        st.subheader("⚙️ Configurações")
        quality = st.slider("Qualidade do PDF (DPI)", min_value=150, max_value=300, value=200, 
                           help="DPI mais alto = melhor qualidade, mas arquivo maior")
        
        # Processar imagem
        if st.button("🔄 Converter para PDF 10x15cm"):
            with st.spinner("Processando imagem e criando PDF..."):
                try:
                    # Salvar imagem temporariamente
                    temp_image_path = "temp_image.jpg"
                    
                    # Converter para RGB se necessário (para PNG com transparência)
                    if image.mode in ('RGBA', 'LA', 'P'):
                        background = Image.new('RGB', image.size, 'white')
                        if image.mode == 'P':
                            image = image.convert('RGBA')
                        background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                        image = background
                    
                    image.save(temp_image_path, "JPEG", quality=95)
                    
                    # Criar PDF
                    output_pdf = "imagem_10x15cm.pdf"
                    
                    # Atualizar DPI baseado no slider
                    global cm_to_pixels
                    original_cm_to_pixels = cm_to_pixels
                    cm_to_pixels = lambda cm, dpi=quality: int(cm * dpi / 2.54)
                    
                    pdf_path = create_10x15_pdf(temp_image_path, output_pdf)
                    
                    # Restaurar função original
                    cm_to_pixels = original_cm_to_pixels
                    
                    # Ler o PDF criado
                    with open(pdf_path, "rb") as f:
                        pdf_bytes = f.read()
                    
                    # Botão para download
                    st.success("✅ PDF criado com sucesso!")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.download_button(
                            label="📥 Baixar PDF",
                            data=pdf_bytes,
                            file_name="imagem_10x15cm.pdf",
                            mime="application/pdf",
                            help="Baixe o PDF pronto para impressão"
                        )
                    
                    with col2:
                        st.info("**Dica:** Imprima em papel A4 e corte nas linhas vermelhas")
                    
                    # Preview do layout
                    st.subheader("📐 Visualização do Layout")
                    st.markdown(f"""
                    **Layout do PDF (DPI: {quality}):**
                    - **Página A4:** 21cm × 29.7cm
                    - **Imagem:** 10cm × 15cm (centralizada)
                    - **Linhas vermelhas:** guias para corte
                    - **Margens:** 
                      - Superior/Inferior: ≈7.35cm cada
                      - Esquerda/Direita: ≈3cm cada
                    """)
                    
                    # Limpar arquivos temporários
                    if os.path.exists(temp_image_path):
                        os.remove(temp_image_path)
                    if os.path.exists(output_pdf):
                        os.remove(output_pdf)
                        
                except Exception as e:
                    st.error(f"❌ Erro ao processar a imagem: {str(e)}")
    
    # Informações adicionais
    with st.expander("💡 Dicas para melhor resultado"):
        st.markdown("""
        - **Resolução ideal:** Use imagens com pelo menos 1200×800 pixels
        - **Proporção:** Imagens com proporção 3:2 (15:10) funcionam melhor sem distorção
        - **Formato:** JPG ou PNG com boa qualidade
        - **Impressão:** Use papel cartão de 200-300g/m² para melhor resultado
        - **Corte:** Use estilete e régua para cortes precisos
        - **Qualidade:** 200-300 DPI para ótima qualidade de impressão
        """)
        
    with st.expander("📏 Sobre as dimensões"):
        st.markdown("""
        **Formato 10×15cm:**
        - Altura: 10cm
        - Largura: 15cm  
        - Proporção: 3:2
        
        **Papel A4:**
        - Altura: 29.7cm
        - Largura: 21cm
        
        **Posicionamento:**
        - A imagem fica centralizada no A4
        - Margens iguais nas laterais
        - Linhas vermelhas indicam onde cortar
        """)

if __name__ == "__main__":
    main()
