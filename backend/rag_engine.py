from langchain_ollama import ChatOllama
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

LLM_MODEL = "deepseek-r1:7b"
FALLBACK_CONTACT = "+144-555-0199"
FALLBACK_EMAIL = "support@hospital.com"

def setup_rag_chain(vector_store):
    llm = ChatOllama(model=LLM_MODEL, temperature=0.2)
    retriever = vector_store.as_retriever(search_kwargs={"k": 2})
    
    system_prompt = (
        "You are a helpful hospital assistant. You are currently talking to a {role}. "
        "Tailor your response appropriately for this role... "
        "Use the provided context to answer the user's question. "
        
        "If you cannot find the exact answer in the context, DO NOT guess or make up information. "
        f"Instead, immediately respond with EXACTLY this: 'I am sorry, I do not have that information. "
        f"Please contact the front desk at {FALLBACK_CONTACT} or escalate to administration at {FALLBACK_EMAIL}.'\n\n"
        
        "Context:\n{context}"
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
    ])
    
    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    return create_retrieval_chain(retriever, question_answer_chain)