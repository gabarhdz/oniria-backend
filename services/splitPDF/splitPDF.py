from langchain_chroma import Chroma
from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
import os, chromadb
from chromadb.config import Settings



# 1. Load documento
loader = PyPDFLoader("./pdfs/Rutinas de sueño.pdf")
document = loader.load()

# 2. Break in chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=0) 
chunked_documents = text_splitter.split_documents(document)

# 3. Embeddings
embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

# 4. Client Chroma Cloud
chroma_client = chromadb.Client(
    Settings(
        chroma_api_impl="chromadb.api.client.CloudClient",
        chroma_server_ssl=True,
        chroma_api_key=os.getenv("CHROMA_API_KEY"),
        tenant=os.getenv("CHROMA_TENANT"),
        database=os.getenv("CHROMA_DATABASE"),
    )
)

# 5. LangChain-Chroma wrapper
vectorstore = Chroma(
    client=chroma_client,
    collection_name="noctiria_knowledge",
    embedding_function=embedding_function,
)

# 6. Addd documentos
vectorstore.add_documents(chunked_documents)
