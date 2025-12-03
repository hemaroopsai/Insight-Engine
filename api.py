import os
import tempfile
from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
import chromadb
from langdetect import detect, LangDetectException
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import create_retrieval_chain, create_history_aware_retriever
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader, PyPDFLoader, TextLoader
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv


load_dotenv()


app = FastAPI(
    title="Insight Engine API",
    description="An API for summarizing and querying web articles and documents.",
    version="2.0.0"
)


class ProcessRequest(BaseModel):
    urls: list[str]

class AskQuestionRequest(BaseModel):
    query: str
    chat_history: list[tuple[str, str]] = []

class SummarizeRequest(BaseModel):
    pass

class AnswerResponse(BaseModel):
    answer: str
    sources: list[str]


try:
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2)
    
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'}
    )
    client = chromadb.Client() 
    COLLECTION_NAME = "insight_engine_collection"
except Exception as e:
    raise RuntimeError(f"Failed to initialize models or DB client: {e}")

def clean_llm_output(answer: str) -> str:
    """Removes the <think> block from the LLM's output."""
    if "</think>" in answer:
        return answer.split("</think>", 1)[-1].strip()
    return answer

def process_and_store_documents(documents):
    """Splits documents and stores them in Chroma DB, replacing the old collection."""
    text_splitter = RecursiveCharacterTextSplitter(
        separators=['\n\n', '\n', '.', ','],
        chunk_size=1000,
        chunk_overlap=200
    )
    docs = text_splitter.split_documents(documents)
    
    try:
        client.delete_collection(name=COLLECTION_NAME)
    except Exception:
        pass
    Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        client=client,
        collection_name=COLLECTION_NAME,
    )



@app.post("/process-urls", status_code=200)
def process_urls(request: ProcessRequest):
    unique_urls = list(set(request.urls))
    if not any(unique_urls):
        raise HTTPException(status_code=400, detail="No URLs provided.")

    try:
        loader = WebBaseLoader(unique_urls)
        data = loader.load()
        process_and_store_documents(data)
        return {"message": "URLs processed successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

@app.post("/process-file", status_code=200)
async def process_file(file: UploadFile = File(...)):
    if not file or not file.filename:
        raise HTTPException(status_code=400, detail="No file provided.")

    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        if file.content_type == 'application/pdf':
            loader = PyPDFLoader(tmp_path)
        elif file.content_type == 'text/plain':
            loader = TextLoader(tmp_path)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type. Please upload a PDF or TXT file.")
        
        data = loader.load()
        process_and_store_documents(data)
        return {"message": f"File '{file.filename}' processed successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

@app.post("/summarize", response_model=AnswerResponse)
def summarize_content(request: SummarizeRequest):
    try:
        vectorstore = Chroma(client=client, collection_name=COLLECTION_NAME, embedding_function=embeddings)
        all_docs = vectorstore.get(include=["documents"])['documents']
        
        if not all_docs:
            raise HTTPException(status_code=400, detail="No content available to summarize. Please process documents first.")

        combined_text = "\n".join(all_docs)

        summarization_prompt = ChatPromptTemplate.from_template("""
        Write a concise summary of the following text. Capture the main points and key information.
        
        Text:
        {context}
        
        Summary:
        """)
        
        summarization_chain = summarization_prompt | llm
        result = summarization_chain.invoke({"context": combined_text})
        
        return AnswerResponse(answer=result.content, sources=["Summary of all processed documents"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred during summarization: {e}")


@app.post("/ask-question", response_model=AnswerResponse)
def ask_question(request: AskQuestionRequest):
  
    greetings = ["hi", "hello", "hey", "namaste", "vanakkam"]
    thanks = ["thanks", "thank you", "thankyou"]
    
    if request.query.lower().strip() in greetings:
        return AnswerResponse(answer="Hello! How can I help you with your documents today?", sources=["Conversational AI"])
    if request.query.lower().strip() in thanks:
        return AnswerResponse(answer="You're welcome! Let me know if you have any other questions.", sources=["Conversational AI"])

    try:
        try:
            language = detect(request.query)
        except LangDetectException:
            language = "en" 

        vectorstore = Chroma(client=client, collection_name=COLLECTION_NAME, embedding_function=embeddings)
        retriever = vectorstore.as_retriever()

     
        retriever_prompt = ChatPromptTemplate.from_messages([
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}"),
            ("user", "Given the above conversation, generate a search query to look up in order to get information relevant to the conversation")
        ])
        
        history_aware_retriever = create_history_aware_retriever(llm, retriever, retriever_prompt)

        
        qa_prompt = ChatPromptTemplate.from_messages([
            ("system", "Answer the user's question based on the below context.\n\n{context}"),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}"),
        ])
        
        document_chain = create_stuff_documents_chain(llm, qa_prompt)
        retrieval_chain = create_retrieval_chain(history_aware_retriever, document_chain)
        

        formatted_history = []
        for human, ai in request.chat_history:
            formatted_history.append({"role": "user", "content": human})
            formatted_history.append({"role": "assistant", "content": ai})

        result = retrieval_chain.invoke({"input": request.query, "chat_history": formatted_history})
        
        sources = list(set(doc.metadata.get('source', 'Unknown') for doc in result.get("context", [])))
        
        return AnswerResponse(answer=result.get("answer", "No answer found."), sources=sources)

    except Exception as e:
        if "does not exist" in str(e) or "got 0 documents" in str(e):
             raise HTTPException(status_code=400, detail="No documents processed yet. Please submit URLs or a file first.")
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
