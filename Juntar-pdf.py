import streamlit as st
from pypdf import PdfMerger
import io

st.set_page_config(page_title="Juntar PDFs", layout="centered")

st.title("📄 Juntar arquivos PDF")

st.write("Envie vários arquivos PDF para gerar um único documento.")

# Upload múltiplo
arquivos_pdf = st.file_uploader(
    "Selecione os PDFs",
    type="pdf",
    accept_multiple_files=True
)

if arquivos_pdf:

    st.write(f"{len(arquivos_pdf)} arquivos carregados.")

    if st.button("🔗 Juntar PDFs"):

        merger = PdfMerger()

        for pdf in arquivos_pdf:
            merger.append(pdf)

        pdf_final = io.BytesIO()
        merger.write(pdf_final)
        merger.close()

        pdf_final.seek(0)

        st.success("PDF gerado com sucesso.")

        st.download_button(
            label="⬇️ Baixar PDF unido",
            data=pdf_final,
            file_name="pdf_unido.pdf",
            mime="application/pdf"
        )
