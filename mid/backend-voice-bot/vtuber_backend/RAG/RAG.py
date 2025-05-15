from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from openai import OpenAI
from vector_database import CustomE5Embedding
import os

embedding_model = CustomE5Embedding(model_name="intfloat/multilingual-e5-small")
db = FAISS.load_local("faiss_db", embedding_model, allow_dangerous_deserialization=True)
retriever = db.as_retriever()

model = "llama3-70b-8192"
base_url="https://api.groq.com/openai/v1"


os.environ["OPENAI_API_KEY"] = "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"

client = OpenAI(
    base_url=base_url # 使用 OpenAI 本身不需要這段
)

system_prompt = "你是金門大學的 AI 助理，請根據資料來回應學生的問題。請親切、簡潔並附帶具體建議。請用台灣習慣的中文回應。"

prompt_template = """
根據下列資料回答問題：
{retrieved_chunks}

使用者的問題是：{question}

請根據資料內容回覆，若資料不足請告訴同學可以請教金門大學的老師。
"""

chat_history = []

def chat_with_rag(user_input):
    global chat_history
    # 取回相關資料
    docs = retriever.get_relevant_documents(user_input)
    retrieved_chunks = "\n\n".join([doc.page_content for doc in docs])

    # 將自定 prompt 套入格式
    final_prompt = prompt_template.format(retrieved_chunks=retrieved_chunks, question=user_input)

    # 呼叫 OpenAI API
    response = client.chat.completions.create(
    model=model,
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": final_prompt},
    ]
    )
    answer = response.choices[0].message.content

    chat_history.append((user_input, answer))
    return answer

response = chat_with_rag("請問金門大學的優缺點?")
print(response)