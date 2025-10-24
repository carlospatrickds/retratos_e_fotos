import streamlit as st
from PIL import Image
from io import BytesIO

st.set_page_config(page_title="Imagens → PDF", page_icon="📄", layout="wide")

st.title("📸 Converter Imagens em PDF")
st.write("Envie suas imagens (JPG ou PNG), altere a ordem, visualize e gere um PDF!")

# --- Estado inicial ---
# Estrutura de dados mais robusta: [{"nome": str, "imagem": Image.Image}, ...]
if "data_imagens" not in st.session_state:
    st.session_state.data_imagens = []
# Set para rastrear arquivos já processados (evita re-adição e rollback)
if "uploaded_file_keys" not in st.session_state:
    st.session_state.uploaded_file_keys = set()

# --- Funções auxiliares ---

def mover_cima(index):
    if index > 0:
        st.session_state.data_imagens[index], st.session_state.data_imagens[index-1] = st.session_state.data_imagens[index-1], st.session_state.data_imagens[index]

def mover_baixo(index):
    if index < len(st.session_state.data_imagens) - 1:
        st.session_state.data_imagens[index], st.session_state.data_imagens[index+1] = st.session_state.data_imagens[index+1], st.session_state.data_imagens[index]

def girar_imagem(index):
    st.session_state.data_imagens[index]["imagem"] = st.session_state.data_imagens[index]["imagem"].rotate(-90, expand=True)

def excluir_imagem(index):
    # Não precisamos mexer no uploaded_file_keys aqui, pois o arquivo pode ser re-adicionado
    # se o usuário fizer upload novamente. Apenas removemos do estado atual.
    del st.session_state.data_imagens[index]

def limpar_tudo():
    st.session_state.data_imagens.clear()
    st.session_state.uploaded_file_keys.clear() 
    # O Streamlit não permite resetar o file_uploader via st.session_state,
    # então removemos a linha problemática e usamos apenas rerun().
    # O estado dos dados já está limpo.
    

# Função para adicionar imagens com verificação robusta
def adicionar_imagens(uploaded_files):
    if not uploaded_files:
        return

    # Usamos o nome do arquivo + seu tamanho como uma chave única de processamento
    for file in uploaded_files:
        # Importante: o objeto file (UploadedFile) é re-criado a cada upload,
        # mas a lista uploaded_files é "sticky" até o usuário interagir.
        file_key = f"{file.name}_{file.size}"
        
        # Só adiciona se o arquivo ainda não foi processado/adicionado
        if file_key not in st.session_state.uploaded_file_keys:
            try:
                # Usar file.seek(0) antes de Image.open() garante que o ponteiro está no início,
                # importante ao lidar com múltiplos uploads ou re-execuções.
                file.seek(0) 
                img = Image.open(file).convert("RGB")
                st.session_state.data_imagens.append({"nome": file.name, "imagem": img})
                st.session_state.uploaded_file_keys.add(file_key)
            except Exception as e:
                st.error(f"Erro ao carregar o arquivo {file.name}: {e}")

# --- Upload ---
uploaded_files = st.file_uploader(
    "Selecione ou arraste suas imagens aqui",
    type=["png", "jpg", "jpeg"],
    accept_multiple_files=True,
    key="image_uploader" # Adicionamos uma chave para controle
)

# Chama a função para processar os arquivos carregados
adicionar_imagens(uploaded_files)

# --- Abas ---
aba1, aba2 = st.tabs(["🗂️ Organizar Imagens", "👀 Pré-visualização"])

# --- ABA 1: ORGANIZAR ---
with aba1:
    st.subheader("🧩 Reordene e edite suas imagens")

    if st.session_state.data_imagens:
        
        # A forma mais robusta de exibir em Streamlit é garantindo a unicidade da key
        # e a correta referência no on_click.
        for i, item in enumerate(st.session_state.data_imagens):
            nome = item["nome"]
            # Usar o container st.container() com uma key única ajuda a isolar os elementos
            # de cada linha do loop.
            with st.container(key=f"item_container_{nome}_{i}"):
                col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 1])

                # Colunas com os botões e texto
                with col1:
                    st.write(f"**{i+1}. {nome}**")

                with col2:
                    st.button("⬆️", key=f"up_{nome}_{i}", on_click=mover_cima, args=(i,))

                with col3:
                    st.button("⬇️", key=f"down_{nome}_{i}", on_click=mover_baixo, args=(i,))

                with col4:
                    st.button("🔄", key=f"rotate_{nome}_{i}", on_click=girar_imagem, args=(i,))

                with col5:
                    st.button("🗑️", key=f"delete_{nome}_{i}", on_click=excluir_imagem, args=(i,))
            
            # Adiciona um divisor leve entre os itens
            st.markdown("---", unsafe_allow_html=False) 

        st.divider()
        
        # Botão Limpar Tudo (Corrigido para evitar o StreamlitAPIException)
        if st.button("🧹 Limpar alterações"):
            limpar_tudo() 
            st.rerun() # Força a re-execução com o estado limpo

    else:
        st.info("Nenhuma imagem carregada ainda. Faça o upload acima.")

# --- ABA 2: PRÉ-VISUALIZAÇÃO ---
with aba2:
    if st.session_state.data_imagens:
        st.subheader("👁️ Visualização das imagens")
        
        # Extrai os dados para visualização e geração de PDF
        imagens_para_visualizar = [item["imagem"] for item in st.session_state.data_imagens]
        nomes_para_visualizar = [item["nome"] for item in st.session_state.data_imagens]
        
        # Exibe no máximo 3 colunas de imagem na pré-visualização
        cols = st.columns(min(3, len(imagens_para_visualizar)))
        for i, img in enumerate(imagens_para_visualizar):
            # Usamos o módulo (%) para ciclar nas colunas (se houver mais de 3 imagens)
            with cols[i % len(cols)]: 
                st.image(img, caption=nomes_para_visualizar[i], use_container_width=True)

        nome_pdf = st.text_input("📝 Nome do PDF (sem .pdf):", value="imagens_unidas")

        if st.button("📄 Gerar PDF"):
            if not imagens_para_visualizar:
                st.error("Não há imagens para gerar o PDF!")
            else:
                pdf_buffer = BytesIO()
                
                primeira_imagem = imagens_para_visualizar[0]
                outras_imagens = imagens_para_visualizar[1:]
                
                # Salva a primeira imagem, anexando as demais.
                primeira_imagem.save(
                    pdf_buffer,
                    format="PDF",
                    save_all=True,
                    append_images=outras_imagens
                )
                pdf_bytes = pdf_buffer.getvalue()

                st.success("✅ PDF gerado com sucesso!")
                st.download_button(
                    label="⬇️ Baixar PDF",
                    data=pdf_bytes,
                    file_name=f"{nome_pdf}.pdf",
                    mime="application/pdf"
                )
    else:
        st.info("Nenhuma imagem para visualizar.")
