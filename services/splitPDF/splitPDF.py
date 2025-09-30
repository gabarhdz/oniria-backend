from langchain_chroma import Chroma
from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
import os, chromadb
from decouple import config
from dotenv import load_dotenv

load_dotenv()

# 1. Load documento
loader = PyPDFLoader("./pdfs/TCC.pdf")
document = loader.load()

# 2. Break in chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=12)
chunked_documents = text_splitter.split_documents(document)
print(f"Chunked doc: {chunked_documents}")

# 3. Embeddings
embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

# 4. Client Chroma Cloud - USA HttpClient en lugar de Client
chroma_client = chromadb.HttpClient(
    host=config("CHROMADB_HOST"),  # Por ejemplo: "api.trychroma.com"
    port=443,  # Puerto SSL
    ssl=True,
    headers={
        "x-chroma-token": config("CHROMADB_API_KEY")
    },
    tenant=config("CHROMADB_TENANT"),
    database=config("CHROMADB_DATABASE"),
)

# 5. LangChain-Chroma wrapper
vectorstore = Chroma(
    client=chroma_client,
    collection_name="noctiria_knowledge",
    embedding_function=embedding_function,
)

# 6. Add documentos
vectorstore.add_documents(chunked_documents)
print(f" {len(chunked_documents)} documentos agregados exitosamente")