from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from embeddings import get_embeddings
from groq import Groq


def process_pdf(file_path):
    loader = PyPDFLoader(file_path)
    documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    docs = text_splitter.split_documents(documents)

    embeddings = get_embeddings()
    vectorstore = FAISS.from_documents(docs, embeddings)
    return vectorstore


def query_pdf(vectorstore, query):
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    docs = retriever.invoke(query)
    context = "\n".join([doc.page_content for doc in docs])

    prompt = f"""Answer ONLY from the context below.
If not found, say 'Not in document'.

Context:
{context}

Question:
{query}

Answer:"""

    client = Groq(api_key="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")

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=512,
        temperature=0.2
    )

    return response.choices[0].message.content