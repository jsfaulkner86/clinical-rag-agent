from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

# ── CONFIGURATION ──────────────────────────────────────

GUIDELINE_PDF = "acog_cpg11_endometriosis.pdf"  # Place PDF in project root
CHROMA_DB_PATH = "./chroma_db"

# ── STEP 1: LOAD & CHUNK DOCUMENT ──────────────────────

def load_and_chunk_guideline(pdf_path: str):
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ".", " "]
    )
    chunks = splitter.split_documents(documents)
    print(f"Loaded {len(documents)} pages → {len(chunks)} chunks")
    return chunks

# ── STEP 2: EMBED & STORE ──────────────────────────────

def build_vector_store(chunks):
    embeddings = OpenAIEmbeddings()
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_DB_PATH
    )
    vectorstore.persist()
    print("Vector store built and persisted.")
    return vectorstore

# ── STEP 3: BUILD RAG CHAIN ────────────────────────────

def build_rag_chain(vectorstore):
    llm = ChatOpenAI(model="gpt-4", temperature=0.1)

    prompt_template = """You are a clinical knowledge assistant trained on 
    ACOG Clinical Practice Guidelines. Answer the clinician's question 
    using only the provided guideline context. If the answer is not 
    in the context, say "This guideline does not address that question directly."

    Context: {context}

    Question: {question}

    Clinical Answer:"""

    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["context", "question"]
    )

    rag_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(search_kwargs={"k": 4}),
        chain_type_kwargs={"prompt": prompt},
        return_source_documents=True
    )
    return rag_chain

# ── STEP 4: QUERY ──────────────────────────────────────

def query_guideline(chain, question: str):
    print(f"\nQuestion: {question}")
    result = chain({"query": question})
    print(f"\nAnswer: {result['result']}")
    print(f"\nSources: {len(result['source_documents'])} chunks retrieved")
    return result

# ── MAIN ──────────────────────────────────────────────

if __name__ == "__main__":
    chunks = load_and_chunk_guideline(GUIDELINE_PDF)
    vectorstore = build_vector_store(chunks)
    chain = build_rag_chain(vectorstore)

    # Sample clinical queries
    test_questions = [
        "What are the presumptive diagnostic criteria for endometriosis under CPG-11?",
        "When is surgical confirmation required for an endometriosis diagnosis?",
        "What first-line treatments does ACOG recommend for endometriosis?"
    ]

    for question in test_questions:
        query_guideline(chain, question)
