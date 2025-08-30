import os
import tempfile
import re
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
    title="Insight Engine: Research API",
    description="An API for processing documents and holding intelligent conversations.",
    version="2.0.0"
)

# --- Pydantic Models ---
class ProcessURLRequest(BaseModel):
    urls: list[str]

class AskQuestionRequest(BaseModel):
    query: str
    chat_history: list[tuple[str, str]] | None = None

class AnswerResponse(BaseModel):
    answer: str
    sources: list[str]

# --- NEW: Pydantic Model for Summarization ---
class SummarizeResponse(BaseModel):
    summary: str

# --- Global Objects ---
try:
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.1)
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/paraphrase-multilingual-mpnet-base-v2",
        model_kwargs={'device': 'cpu'}
    )
    client = chromadb.Client()
    COLLECTION_NAME = "insight_engine_collection"
except Exception as e:
    raise RuntimeError(f"Failed to initialize models or DB client: {e}")

# --- Helper Functions ---
def clean_llm_output(answer: str) -> str:
    match = re.search(r"</think>(.*)", answer, re.DOTALL)
    if match:
        return match.group(1).strip()
    return answer

def process_documents_logic(documents):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    docs = text_splitter.split_documents(documents)
    try:
        client.delete_collection(name=COLLECTION_NAME)
    except Exception:
        pass
    Chroma.from_documents(
        documents=docs, embedding=embeddings, client=client, collection_name=COLLECTION_NAME
    )

def handle_greetings(query: str) -> str | None:
    greetings = ["hi", "hello", "hey", "good morning", "good afternoon", "good evening"]
    thanks = ["thanks", "thank you", "thx"]
    if query.lower().strip() in greetings:
        return "Hello! How can I help you with your documents today?"
    if query.lower().strip() in thanks:
        return "You're welcome!"
    return None

# --- API Endpoints ---
@app.post("/process-urls", status_code=200)
def process_urls(request: ProcessURLRequest):
    unique_urls = list(set(url for url in request.urls if url))
    if not unique_urls:
        raise HTTPException(status_code=400, detail="No valid URLs provided.")
    try:
        loader = WebBaseLoader(unique_urls)
        data = loader.load()
        process_documents_logic(data)
        return {"message": "URLs processed successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

@app.post("/process-file", status_code=200)
async def process_file(file: UploadFile = File(...)):
    if not file or not file.filename:
        raise HTTPException(status_code=400, detail="No file provided.")
    
    suffix = os.path.splitext(file.filename)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name
    
    try:
        if file.content_type == 'application/pdf':
            loader = PyPDFLoader(tmp_path)
        elif file.content_type == 'text/plain':
            loader = TextLoader(tmp_path)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type.")
        
        data = loader.load()
        process_documents_logic(data)
        return {"message": f"File '{file.filename}' processed successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {e}")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

# --- NEW: Summarization Endpoint ---
@app.post("/summarize", response_model=SummarizeResponse)
def summarize_documents():
    try:
        vectorstore = Chroma(
            client=client,
            collection_name=COLLECTION_NAME,
            embedding_function=embeddings,
        )
        # Fetch all documents from the collection
        all_docs = vectorstore.get()["documents"]
        if not all_docs:
            raise HTTPException(status_code=400, detail="No documents found to summarize.")

        # Create a summarization chain
        prompt_template = """Write a concise summary of the following text, capturing the main points:

        "{text}"

        CONCISE SUMMARY:"""
        prompt = ChatPromptTemplate.from_template(prompt_template)
        
        summarization_chain = prompt | llm

        # Join all docs into a single string to summarize
        full_text = "\n\n".join(all_docs)
        
        summary_result = summarization_chain.invoke({"text": full_text})
        
        return SummarizeResponse(summary=summary_result.content)
    except Exception as e:
        if "does not exist" in str(e):
             raise HTTPException(status_code=400, detail="No documents have been processed yet.")
        raise HTTPException(status_code=500, detail=f"An error occurred during summarization: {e}")


@app.post("/ask-question", response_model=AnswerResponse)
def ask_question(request: AskQuestionRequest):
    greeting_response = handle_greetings(request.query)
    if greeting_response:
        return AnswerResponse(answer=greeting_response, sources=[])

    try:
        language = detect(request.query)
    except LangDetectException:
        language = "en"
    
    try:
        vectorstore = Chroma(client=client, collection_name=COLLECTION_NAME, embedding_function=embeddings)
        retriever = vectorstore.as_retriever()

        # Contextualize question prompt
        contextualize_q_system_prompt = """Given a chat history and the latest user question \
        which might reference context in the chat history, formulate a standalone question \
        which can be understood without the chat history. Do NOT answer the question, \
        just reformulate it if needed and otherwise return it as is."""
        contextualize_q_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", contextualize_q_system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )
        history_aware_retriever = create_history_aware_retriever(
            llm, retriever, contextualize_q_prompt
        )

        # Answer question prompt
        qa_system_prompt = f"""Use the following pieces of context to answer the user's question. \
        If you don't know the answer, just say that you don't know. \
        Provide only the direct answer to the question, without any of your thought process or preamble. \
        Answer in the following language: {language}

        Context:
        {{context}}
        
        Final Answer:"""
        qa_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", qa_system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )

        question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
        rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

        result = rag_chain.invoke({"input": request.query, "chat_history": request.chat_history or []})
        
        clean_answer = clean_llm_output(result.get("answer", "No answer found."))
        sources = list(set(doc.metadata.get('source', 'Unknown') for doc in result.get("context", [])))
        
        return AnswerResponse(answer=clean_answer, sources=sources)

    except Exception as e:
        if "does not exist" in str(e):
            raise HTTPException(status_code=400, detail="No documents processed. Please upload a file or process URLs first.")
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
