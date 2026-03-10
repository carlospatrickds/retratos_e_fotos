import streamlit as st
from pypdf import PdfMerger, PdfReader
import io

st.set_page_config(page_title="Juntar PDFs", layout="centered")

st.title("📄 Juntar Arquivos PDF")

st.write("Envie vários PDFs, organize a ordem e gere um único arquivo.")

# Upload de arquivos
uploaded_files = st.file_uploader(
    "Selecione os PDFs",
    type="pdf",
    accept_multiple_files=True
)

if uploaded_files:

    st.subheader("Arquivos carregados")

    arquivos = []

    for file in uploaded_files:
        reader = PdfReader(file)
        paginas = len(reader.pages)

        arquivos.append({
            "nome": file.name,
            "file": file,
            "paginas": paginas
        })

    # Controle de ordem
    for i, arq in enumerate(arquivos):

        col1, col2, col3 = st.columns([4,1,1])

        with col1:
            st.write(f"**{i+1}. {arq['nome']}** ({arq['paginas']} páginas)")

        with col2:
            if st.button("⬆", key=f"up{i}") and i > 0:
                arquivos[i], arquivos[i-1] = arquivos[i-1], arquivos[i]
                st.rerun()

        with col3:
            if st.button("⬇", key=f"down{i}") and i < len(arquivos)-1:
                arquivos[i], arquivos[i+1] = arquivos[i+1], arquivos[i]
                st.rerun()

    st.divider()

    if st.button("🔗 Juntar PDFs"):

        merger = PdfMerger()

        progress = st.progress(0)

        for i, arq in enumerate(arquivos):

            merger.append(arq["file"])

            progresso = (i + 1) / len(arquivos)
            progress.progress(progresso)

        pdf_final = io.BytesIO()
        merger.write(pdf_final)
        merger.close()

        pdf_final.seek(0)

        st.success("PDF gerado com sucesso.")

        st.download_button(
            label="⬇ Baixar PDF unido",
            data=pdf_final,
            file_name="pdf_unificado.pdf",
            mime="application/pdf"
        )
