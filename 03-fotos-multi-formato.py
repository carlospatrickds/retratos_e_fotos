# app_fotos_multiformato.py
# Streamlit app: "Fotos Multi-Formato"
# - Transforma qualquer foto em formatos 9x12, 9x13, 8x10 dentro de 10x15
# - Permite editar dimensões customizadas
# - Otimizado para fotos de celular

import streamlit as st
from PIL import Image, ImageOps, ImageDraw
import io
import math

st.set_page_config(page_title="Fotos Multi-Formato", layout="centered")
st.title("🖼️ Fotos Multi-Formato")
st.write("Transforme suas fotos de celular em múltiplos formatos dentro da folha 10×15 cm")

# Funções utilitárias
def cm_to_px(cm, dpi):
    return int(round(cm * dpi / 2.54))

def mm_to_px(mm, dpi):
    return int(round(mm * dpi / 25.4))

def make_print_image(img, target_size_px, background_color=(255, 255, 255)):
    """Redimensiona a imagem para caber no target mantendo proporção"""
    img_ratio = img.width / img.height
    target_ratio = target_size_px[0] / target_size_px[1]
    
    if img_ratio > target_ratio:
        # Imagem mais larga - ajusta pela altura
        new_height = target_size_px[1]
        new_width = int(img_ratio * new_height)
    else:
        # Imagem mais alta - ajusta pela largura
        new_width = target_size_px[0]
        new_height = int(new_width / img_ratio)
    
    img_resized = img.resize((new_width, new_height), Image.LANCZOS)
    
    # Cria fundo branco
    background = Image.new('RGB', target_size_px, background_color)
    
    # Centraliza a imagem
    x_offset = (target_size_px[0] - new_width) // 2
    y_offset = (target_size_px[1] - new_height) // 2
    
    background.paste(img_resized, (x_offset, y_offset))
    return background

def create_layout_10x15(images, dpi=300):
    """Cria layout com múltiplas imagens em folha 10x15"""
    w_10x15 = cm_to_px(10, dpi)
    h_10x15 = cm_to_px(15, dpi)
    
    layout = Image.new('RGB', (w_10x15, h_10x15), (255, 255, 255))
    draw = ImageDraw.Draw(layout)
    
    # Posições iniciais
    x, y = 0, 0
    max_y = 0
    
    for i, (img, label, size_cm) in enumerate(images):
        # Adiciona margem entre imagens
        if i > 0:
            x += mm_to_px(5, dpi)  # 5mm de espaçamento
        
        # Verifica se cabe na linha
        if x + img.width > w_10x15:
            x = 0
            y = max_y + mm_to_px(5, dpi)
        
        layout.paste(img, (x, y))
        
        # Desenha borda e label
        draw.rectangle([x, y, x + img.width, y + img.height], outline=(200, 200, 200), width=1)
        draw.text((x + 5, y + 5), f"{label} ({size_cm[0]}×{size_cm[1]}cm)", fill=(100, 100, 100))
        
        x += img.width
        max_y = max(max_y, y + img.height)
    
    return layout

# Configurações principais
st.sidebar.header("⚙️ Configurações")

DPI = st.sidebar.select_slider(
    "Resolução (DPI)",
    options=[150, 200, 250, 300, 350, 400],
    value=300,
    help="Maior DPI = melhor qualidade para impressão"
)

background_color = st.sidebar.color_picker(
    "Cor do fundo",
    "#FFFFFF",
    help="Cor do fundo para áreas não preenchidas pela foto"
)

# Formatos pré-definidos
FORMATOS_PREDEFINIDOS = {
    "9×12 cm": (9, 12),
    "9×13 cm": (9, 13), 
    "8×10 cm": (8, 10),
    "7×10 cm": (7, 10),
    "6×9 cm": (6, 9),
    "5×7 cm": (5, 7),
}

# UI principal
uploaded_file = st.file_uploader(
    "📸 Faça upload da sua foto",
    type=["jpg", "jpeg", "png", "webp", "heic"],
    help="Selecione uma foto do seu celular ou computador"
)

if uploaded_file:
    try:
        # Carregar imagem
        original_img = Image.open(uploaded_file).convert('RGB')
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📷 Foto Original")
            st.image(original_img, use_column_width=True)
            st.write(f"**Dimensões:** {original_img.width} × {original_img.height} pixels")
        
        with col2:
            st.subheader("🎯 Formatos Disponíveis")
            
            # Seleção de formatos
            formatos_selecionados = []
            for formato, dimensoes in FORMATOS_PREDEFINIDOS.items():
                if st.checkbox(formato, value=True):
                    formatos_selecionados.append((formato, dimensoes))
            
            # Formato customizado
            st.markdown("---")
            st.subheader("📐 Formato Customizado")
            custom_ativa = st.checkbox("Adicionar formato customizado")
            
            if custom_ativa:
                col_c1, col_c2 = st.columns(2)
                with col_c1:
                    custom_largura = st.number_input("Largura (cm)", min_value=1.0, max_value=10.0, value=7.0, step=0.5)
                with col_c2:
                    custom_altura = st.number_input("Altura (cm)", min_value=1.0, max_value=15.0, value=10.0, step=0.5)
                
                if custom_largura > 0 and custom_altura > 0:
                    formatos_selecionados.append((f"Custom {custom_largura}×{custom_altura}cm", (custom_largura, custom_altura)))
        
        if formatos_selecionados:
            st.subheader("🖼️ Prévia dos Formatos")
            
            # Processar cada formato selecionado
            imagens_processadas = []
            
            for formato_nome, dimensoes in formatos_selecionados:
                largura_cm, altura_cm = dimensoes
                largura_px = cm_to_px(largura_cm, DPI)
                altura_px = cm_to_px(altura_cm, DPI)
                
                # Processar imagem para o formato
                img_formatada = make_print_image(
                    original_img, 
                    (largura_px, altura_px),
                    background_color=background_color
                )
                
                imagens_processadas.append((img_formatada, formato_nome, (largura_cm, altura_cm)))
            
            # Criar layout da folha 10x15
            folha_10x15 = create_layout_10x15(imagens_processadas, DPI)
            
            st.image(folha_10x15, caption="Layout na folha 10×15 cm", use_column_width=True)
            
            st.subheader("📥 Download")
            
            # Download da folha completa
            buf_folha = io.BytesIO()
            folha_10x15.save(buf_folha, format='JPEG', quality=95, dpi=(DPI, DPI))
            buf_folha.seek(0)
            
            st.download_button(
                "📄 Baixar Folha 10×15 Completa",
                buf_folha,
                f"folha_fotos_{DPI}dpi.jpg",
                "image/jpeg",
                help="Baixe a folha completa com todos os formatos selecionados"
            )
            
            # Downloads individuais
            st.markdown("**Downloads Individuais:**")
            cols_download = st.columns(min(3, len(imagens_processadas)))
            
            for idx, (img, formato_nome, dimensoes) in enumerate(imagens_processadas):
                col_idx = idx % 3
                with cols_download[col_idx]:
                    buf_individual = io.BytesIO()
                    img.save(buf_individual, format='JPEG', quality=95, dpi=(DPI, DPI))
                    buf_individual.seek(0)
                    
                    nome_arquivo = f"foto_{formato_nome.replace(' ', '_').replace('×', 'x')}_{DPI}dpi.jpg"
                    
                    st.download_button(
                        f"⬇️ {formato_nome}",
                        buf_individual,
                        nome_arquivo,
                        "image/jpeg",
                        key=f"download_{idx}"
                    )
            
            # Informações técnicas
            with st.expander("📊 Informações Técnicas"):
                st.markdown(f"""
                **Configurações aplicadas:**
                - Resolução: {DPI} DPI
                - Cor do fundo: {background_color}
                - Folha base: 10×15 cm ({cm_to_px(10, DPI)} × {cm_to_px(15, DPI)} pixels)
                - Formatos gerados: {len(formatos_selecionados)}
                
                **Formatos incluídos:**
                {chr(10).join([f"- {nome} ({dims[0]}×{dims[1]}cm)" for nome, dims in formatos_selecionados])}
                
                **Instruções para impressão:**
                1. Baixe a folha completa ou os formatos individuais
                2. Imprima em papel fotográfico 10×15 cm
                3. Certifique-se de que a impressora não aplica cortes automáticos
                4. Recorte seguindo as linhas de guia
                """)
        
        else:
            st.warning("⚠️ Selecione pelo menos um formato para processar.")
    
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
    # Tela inicial
    st.info("""
    ### 👆 Faça upload de uma foto para começar!
    
    **Formatos suportados:** JPG, JPEG, PNG, WEBP, HEIC
    
    **Formatos disponíveis:**
    - 9×12 cm
    - 9×13 cm  
    - 8×10 cm
    - 7×10 cm
    - 6×9 cm
    - 5×7 cm
    - E formato customizado!
    
    **Como usar:**
    1. Faça upload da foto
    2. Selecione os formatos desejados
    3. Ajuste DPI e cor do fundo se necessário
    4. Visualize o layout na folha 10×15
    5. Baixe a folha completa ou formatos individuais
    
    **💡 Dica:** Use 300 DPI para melhor qualidade de impressão!
    """)
    
    # Exemplo visual dos formatos
    st.subheader("📐 Exemplo de Layout na Folha 10×15")
    
    # Criar imagem de exemplo
    exemplo_img = Image.new('RGB', (600, 400), (240, 240, 240))
    draw = ImageDraw.Draw(exemplo_img)
    
    # Desenhar retângulos representando os formatos
    formatos_exemplo = [(100, 150, "9×12"), (100, 162, "9×13"), (80, 100, "8×10")]
    pos_x, pos_y = 50, 50
    
    for largura, altura, label in formatos_exemplo:
        draw.rectangle([pos_x, pos_y, pos_x + largura, pos_y + altura], 
                      outline=(100, 100, 100), width=2, fill=(220, 220, 220))
        draw.text((pos_x + 10, pos_y + 10), label, fill=(100, 100, 100))
        pos_x += largura + 20
    
    st.image(exemplo_img, caption="Exemplo de organização dos formatos na folha", use_column_width=True)

st.markdown("---")
st.caption("🛠️ Desenvolvido: Fotos Multi-Formato - Otimizado para impressão 10×15 cm")
