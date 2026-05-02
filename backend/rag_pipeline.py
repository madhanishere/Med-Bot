import os
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_community.vectorstores import FAISS
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate


def load_and_chunk_document(file_path: str):
    print(f"Loading document from: {file_path}")
    loader = TextLoader(file_path)
    documents = loader.load()
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=150, chunk_overlap=30)
    return text_splitter.split_documents(documents)


def create_vector_store(chunks):
    print("Generating embeddings and building FAISS database...")

    embeddings = OllamaEmbeddings(model="mxbai-embed-large")
    

    vector_store = FAISS.from_documents(chunks, embeddings)
    

    db_path = os.path.join("..", "data", "vector_store")
    vector_store.save_local(db_path)
    print(f"FAISS database saved to {db_path}")
    
    return vector_store


def setup_rag_chain(vector_store):

    llm = ChatOllama(model="deepseek-r1:7b", temperature=0.2)
    

    retriever = vector_store.as_retriever(search_kwargs={"k": 2})
    

    system_prompt = (
        "You are a helpful hospital assistant. Use the provided context to answer the user's question. "
        "If you don't know the answer, just say that you don't know. Do not make up information.\n\n"
        "Context:\n{context}"
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
    ])
    

    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)
    
    return rag_chain

if __name__ == "__main__":
    sample_file = os.path.join("..", "data", "raw_documents", "sample.txt")
    
    try:

        document_chunks = load_and_chunk_document(sample_file)
        

        vector_store = create_vector_store(document_chunks)
        

        rag_chain = setup_rag_chain(vector_store)
        

        test_question = "OP timings"
        print(f"\nAsking: {test_question}")
        print("Thinking...\n")
        
        response = rag_chain.invoke({"input": test_question})
        
        print(f"Answer: {response['answer']}")
        
    except Exception as e:
        print(f"Error: {e}")