import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io
import tempfile
import os

def criar_mascara_meia_lua(largura, altura, altura_arco):
    """
    Cria uma máscara em formato de meia-lua (semicírculo superior)
    """
    mascara = np.zeros((altura, largura), dtype=np.uint8)
    
    centro_x = largura // 2
    raio = altura_arco
    
    # Criar coordenadas de grid
    y_coords, x_coords = np.ogrid[:altura, :largura]
    
    # Calcular distâncias
    dist_x = np.abs(x_coords - centro_x)
    dist_y = np.abs(altura_arco - y_coords)
    
    # Criar máscara do semicírculo
    mascara_circular = (dist_x**2 + dist_y**2) <= raio**2
    mascara[:altura_arco, :] = mascara_circular[:altura_arco, :] * 255
    
    return mascara

def processar_imagem(imagem, largura_pr, altura_total_pr, altura_arco_pr):
    """
    Processa a imagem para o formato do porta-retrato
    """
    # Converter PIL para numpy array
    img_array = np.array(imagem)
    
    # Converter RGB para BGR (OpenCV)
    if len(img_array.shape) == 3 and img_array.shape[2] == 3:
        img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
    
    altura_img, largura_img = img_array.shape[:2]
    
    # Calcular escala para preencher toda a área
    escala_largura = largura_pr / largura_img
    escala_altura = altura_total_pr / altura_img
    escala = max(escala_largura, escala_altura)
    
    nova_largura = int(largura_img * escala)
    nova_altura = int(altura_img * escala)
    
    img_redimensionada = cv2.resize(img_array, (nova_largura, nova_altura))
    
    # Recortar o centro
    inicio_x = max(0, (nova_largura - largura_pr) // 2)
    inicio_y = max(0, (nova_altura - altura_total_pr) // 2)
    
    img_recortada = img_redimensionada[inicio_y:inicio_y+altura_total_pr, 
                                     inicio_x:inicio_x+largura_pr]
    
    # Garantir que a imagem tenha o tamanho exato
    if img_recortada.shape[0] < altura_total_pr or img_recortada.shape[1] < largura_pr:
        img_final = np.zeros((altura_total_pr, largura_pr, 3), dtype=np.uint8)
        y_offset = (altura_total_pr - img_recortada.shape[0]) // 2
        x_offset = (largura_pr - img_recortada.shape[1]) // 2
        img_final[y_offset:y_offset+img_recortada.shape[0], 
                 x_offset:x_offset+img_recortada.shape[1]] = img_recortada
    else:
        img_final = img_recortada
    
    # Criar e aplicar máscara
    mascara = criar_mascara_meia_lua(largura_pr, altura_total_pr, altura_arco_pr)
    resultado = cv2.bitwise_and(img_final, img_final, mask=mascara)
    
    # Converter BGR para RGB
    resultado_rgb = cv2.cvtColor(resultado, cv2.COLOR_BGR2RGB)
    
    return resultado_rgb, mascara

def main():
    st.set_page_config(
        page_title="Porta-Retrato Meia Lua",
        page_icon="🌙",
        layout="wide"
    )
    
    st.title("🌙 Porta-Retrato Formato Meia Lua")
    st.markdown("""
    ### Transforme suas fotos para caber no porta-retrato em formato de arco-íris!
    
    **Dimensões:** 10cm (base) × 15cm (altura total) × 6,5cm (altura do arco)
    """)
    
    # Sidebar para configurações
    st.sidebar.header("Configurações")
    
    # Upload da imagem
    uploaded_file = st.sidebar.file_uploader(
        "📷 Faça upload da sua foto",
        type=['jpg', 'jpeg', 'png', 'bmp'],
        help="Selecione uma imagem do seu celular ou computador"
    )
    
    # Configurações de DPI
    dpi = st.sidebar.slider(
        "Resolução (DPI para impressão)",
        min_value=72,
        max_value=300,
        value=150,
        help="Maior DPI = melhor qualidade para impressão"
    )
    
    # Visualizar máscara
    mostrar_mascara = st.sidebar.checkbox("Mostrar máscara de corte", value=True)
    
    if uploaded_file is not None:
        try:
            # Carregar imagem
            image = Image.open(uploaded_file)
            
            # Mostrar imagem original
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📸 Foto Original")
                st.image(image, use_column_width=True)
                st.write(f"**Dimensões originais:** {image.size[0]} × {image.size[1]} pixels")
            
            # Processar imagem
            with st.spinner("Processando imagem para o porta-retrato..."):
                # Converter cm para pixels
                largura_pr = int(10 * dpi / 2.54)  # 10cm
                altura_total_pr = int(15 * dpi / 2.54)  # 15cm
                altura_arco_pr = int(6.5 * dpi / 2.54)  # 6.5cm
                
                resultado, mascara = processar_imagem(
                    image, largura_pr, altura_total_pr, altura_arco_pr
                )
                
                # Converter resultado para PIL
                resultado_pil = Image.fromarray(resultado)
                
                # Salvar em buffer para download
                img_buffer = io.BytesIO()
                resultado_pil.save(img_buffer, format='JPEG', quality=95)
                img_buffer.seek(0)
            
            with col2:
                st.subheader("🎨 Resultado Final")
                st.image(resultado_pil, use_column_width=True)
                st.write(f"**Dimensões finais:** {largura_pr} × {altura_total_pr} pixels")
                st.write(f"**Altura do arco:** {altura_arco_pr} pixels")
                
                # Botão de download
                st.download_button(
                    label="📥 Download da Imagem Processada",
                    data=img_buffer,
                    file_name=f"porta_retrato_meia_lua_{dpi}dpi.jpg",
                    mime="image/jpeg",
                    help="Clique para baixar a imagem no formato do porta-retrato"
                )
            
            # Mostrar máscara se solicitado
            if mostrar_mascara:
                st.subheader("🔍 Visualização da Máscara")
                col3, col4 = st.columns(2)
                
                with col3:
                    st.image(mascara, caption="Máscara de Corte", use_column_width=True)
                
                with col4:
                    # Sobreposição da máscara
                    overlay = resultado.copy()
                    overlay[mascara == 0] = [255, 0, 0]  # Área cortada em vermelho
                    st.image(overlay, caption="Área Visível (Verde) vs Cortada (Vermelho)", 
                           use_column_width=True)
            
            # Informações técnicas
            with st.expander("📋 Informações Técnicas"):
                st.markdown(f"""
                **Configurações aplicadas:**
                - Dimensões do porta-retrato: 10 × 15 cm
                - Altura do arco: 6,5 cm
                - Resolução: {dpi} DPI
                - Dimensões em pixels: {largura_pr} × {altura_total_pr}
                - Formato: JPEG
                - Qualidade: 95%
                
                **Instruções para impressão:**
                1. Faça o download da imagem
                2. Imprima em papel fotográfico 10×15cm
                3. Certifique-se de que a impressora não está aplicando cortes automáticos
                4. A área vermelha será cortada pelo formato do porta-retrato
                """)
        
        except Exception as e:
            st.error(f"❌ Erro ao processar a imagem: {str(e)}")
            st.info("""
            **Dicas para resolver problemas:**
            - Tente usar uma imagem com formato JPG ou PNG
            - Verifique se o arquivo não está corrompido
            - Tente uma imagem com resolução menor
            - Recarregue a página e tente novamente
            """)
    
    else:
        # Tela inicial quando não há upload
        st.info("""
        ### 👆 Faça upload de uma foto para começar!
        
        **Formatos suportados:** JPG, JPEG, PNG, BMP
        
        **Como usar:**
        1. Clique em "Browse files" ou arraste uma imagem para a área de upload
        2. Ajuste a resolução DPI se necessário (150 DPI é recomendado para impressão)
        3. Visualize o resultado
        4. Faça o download da imagem processada
        5. Imprima em papel fotográfico 10×15cm
        
        **O aplicativo fará automaticamente:**
        - Redimensionamento mantendo a proporção
        - Centralização da imagem
        - Aplicação do formato meia-lua
        - Preparação para impressão
        """)
        
        # Exemplo de visualização
        st.subheader("📐 Visualização do Formato do Porta-Retrato")
        
        # Criar imagem de exemplo
        col1, col2 = st.columns(2)
        
        with col1:
            st.image("https://via.placeholder.com/400x600/4A90E2/FFFFFF?text=10x15cm\nBase=10cm\nArco=6.5cm", 
                    caption="Dimensões: 10cm × 15cm", use_column_width=True)
        
        with col2:
            st.markdown("""
            **Especificações:**
            - **Base:** 10 cm
            - **Altura total:** 15 cm  
            - **Altura do arco:** 6,5 cm
            - **Formato:** Meia-lua (semicírculo superior)
            
            **Área visível:** A parte superior da foto terá formato curvado
            **Área cortada:** As bordas laterais inferiores serão visíveis
            """)

if __name__ == "__main__":
    main()
