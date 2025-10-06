import os
import tempfile

from decouple import config
from dotenv import load_dotenv
from django.utils.deconstruct import deconstructible

import chromadb

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain_community.document_loaders import PyPDFium2Loader
from langchain_chroma import Chroma

# set dotenv
load_dotenv()

@deconstructible
class splitPDF:
    def __call__(self, pdfFile):
        tmp_path = None
        try:
            # Save pdf
            pdf_bytes = pdfFile.read()
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(pdf_bytes)
                tmp_path = tmp.name

            # Load pdf with pyPDFium2Loader
            loader = PyPDFium2Loader(tmp_path)
            document = loader.load()

            # divide in chunks
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=12)
            chunked_documents = text_splitter.split_documents(document)
            print(f"✅ Chunked doc: {len(chunked_documents)} fragmentos")

            # create embedding function
            embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

            # connect to chromadb
            chroma_client = chromadb.HttpClient(
                host=config("CHROMADB_HOST"),
                port=443,
                ssl=True,
                headers={"x-chroma-token": config("CHROMADB_API_KEY")},
                tenant=config("CHROMADB_TENANT"),
                database=config("CHROMADB_DATABASE"),
            )

            # connect to vector store in chroma called "noctiria_knowledge"
            vectorstore = Chroma(
                client=chroma_client,
                collection_name="noctiria_knowledge",
                embedding_function=embedding_function,
            )

            # Upload chunked documents to chromadb
            vectorstore.add_documents(chunked_documents)
            print(f"Documents succesfully added to ChromaDB collection 'noctiria_knowledge'.")

        finally:
            # Delete temp file create in pdf
            if tmp_path and os.path.exists(tmp_path):
                os.remove(tmp_path)
                print(f"Temp file deleted {tmp_path}")

