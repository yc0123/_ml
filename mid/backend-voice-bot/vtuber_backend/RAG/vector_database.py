from langchain_community.document_loaders import TextLoader, PyPDFLoader, UnstructuredWordDocumentLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
import os

class CustomE5Embedding(HuggingFaceEmbeddings):
    def embed_documents(self, texts):
        texts = [f"passage: {t}" for t in texts]
        return super().embed_documents(texts)

    def embed_query(self, text):
        return super().embed_query(f"query: {text}")

folder_path = "uploaded_docs"
documents = []
for file in os.listdir(folder_path):
    path = os.path.join(folder_path, file)
    if file.endswith(".txt"):
        loader = TextLoader(path)
    elif file.endswith(".pdf"):
        loader = PyPDFLoader(path)
    elif file.endswith(".docx"):
        loader = UnstructuredWordDocumentLoader(path)
    else:
        continue
    documents.extend(loader.load())

splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
split_docs = splitter.split_documents(documents)

embedding_model = CustomE5Embedding(model_name="intfloat/multilingual-e5-small")
vectorstore = FAISS.from_documents(split_docs, embedding_model)

vectorstore.save_local("faiss_db")