import streamlit as st
from PIL import Image
import io
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

def cm_to_points(cm):
    """Converte centímetros para pontos (unidade do PDF)"""
    return cm * 28.3465

def create_10x15_pdf(image_path, output_path):
    """Cria um PDF A4 com a imagem no formato 10x15cm centralizada"""
    
    # Tamanhos em pontos
    a4_width, a4_height = A4
    img_width = cm_to_points(15)  # 15cm em pontos
    img_height = cm_to_points(10) # 10cm em pontos
    
    # Calcular posição para centralizar
    x_pos = (a4_width - img_width) / 2
    y_pos = (a4_height - img_height) / 2
    
    # Criar PDF
    c = canvas.Canvas(output_path, pagesize=A4)
    
    # Adicionar a imagem
    img = ImageReader(image_path)
    c.drawImage(img, x_pos, y_pos, img_width, img_height)
    
    # Adicionar guias de corte (opcional)
    c.setStrokeColorRGB(1, 0, 0)  # Vermelho
    c.setLineWidth(0.5)
    
    # Linha superior
    c.line(x_pos, y_pos + img_height, x_pos + img_width, y_pos + img_height)
    # Linha inferior
    c.line(x_pos, y_pos, x_pos + img_width, y_pos)
    # Linha esquerda
    c.line(x_pos, y_pos, x_pos, y_pos + img_height)
    # Linha direita
    c.line(x_pos + img_width, y_pos, x_pos + img_width, y_pos + img_height)
    
    # Adicionar texto informativo
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica", 8)
    c.drawString(50, 50, f"Imagem: 10x15cm - Corte nas linhas vermelhas")
    
    c.save()
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
            st.metric("Formato", image.format)
        
        # Processar imagem
        if st.button("🔄 Converter para PDF 10x15cm"):
            with st.spinner("Processando imagem e criando PDF..."):
                try:
                    # Salvar imagem temporariamente
                    temp_image_path = "temp_image.jpg"
                    image.save(temp_image_path)
                    
                    # Criar PDF
                    output_pdf = "imagem_10x15cm.pdf"
                    pdf_path = create_10x15_pdf(temp_image_path, output_pdf)
                    
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
                    st.subheader("📐 Visualização do Layout no A4")
                    st.markdown("""
                    **Layout do PDF:**
                    - Página A4 (21cm x 29.7cm)
                    - Imagem centralizada: 10cm x 15cm
                    - Linhas vermelhas: guias para corte
                    - Margem superior/inferior: ≈7.35cm cada
                    - Margem esquerda/direita: ≈3cm cada
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
        - **Resolução ideal:** Use imagens com pelo menos 1200x800 pixels
        - **Proporção:** Imagens com proporção 3:2 funcionam melhor
        - **Formato:** JPG ou PNG com boa qualidade
        - **Impressão:** Use papel cartão de 200-300g/m² para melhor resultado
        - **Corte:** Use estilete e régua para cortes precisos
        """)

if __name__ == "__main__":
    main()
