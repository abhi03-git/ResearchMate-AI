from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter
import faiss
import numpy as np
import streamlit as st
from pypdf import PdfReader
from google import genai
from dotenv import load_dotenv
import os

#load .env
load_dotenv()

# Check if API key is loaded
#if os.getenv("GOOGLE_API_KEY"):
#    st.success("API Key Loaded Successfully")
#else:
#   st.error("API Key Not Found")

# Gemini API Key
client = genai.Client(
    api_key=os.getenv("GOOGLE_API_KEY")
)
MODEL_NAME = "gemini-2.5-flash"

# Sidebar
st.sidebar.title("📚 ResearchMate AI")

st.sidebar.info(
    """
    AI-powered Research Assistant

    Features:
    • Paper Summarization
    • Literature Survey
    • Research Gap Detection
    • Semantic Search
    • RAG-based Q&A
    """
)
st.title("📚 ResearchMate AI")

uploaded_file = st.file_uploader(
    "Upload Research Paper",
    type=["pdf"]
)

if uploaded_file:

    reader = PdfReader(uploaded_file)

    text = ""

    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:
            text += page_text

    st.success("PDF loaded successfully!")

    st.subheader("Paper Preview")

    st.write(text[:1500])
    # Process paper only once

    if "processed" not in st.session_state:
        splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
        )
    
        chunks = splitter.split_text(text)
    
        embedding_model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )
    
        embeddings = embedding_model.encode(
            chunks,
            show_progress_bar=False
        )
    
        index = faiss.IndexFlatL2(
            embeddings.shape[1]
        )
    
        index.add(np.array(embeddings))
    
        st.session_state.chunks = chunks
        st.session_state.embedding_model = embedding_model
        st.session_state.index = index
    
        st.session_state.processed = True

    if st.button("Generate Summary"):

        with st.spinner("Generating summary..."):

            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=f"""
                Summarize this research paper:

                {text[:12000]}
                """
            )

            st.subheader("Summary")
    
            st.write(response.text)

            st.download_button(
            "⬇️ Download Summary",
            response.text,
            file_name="paper_summary.txt",
            mime="text/plain"
            )
            
    # -----------------------------
    # Chat with Research Paper
    # -----------------------------

    st.subheader("💬 Chat with Paper")
    
    question = st.text_input(
        "Ask a question about the paper"
    )
    
    if question:
    
        with st.spinner("Searching paper..."):
    
            chunks = st.session_state.chunks
    
            embedding_model = st.session_state.embedding_model
    
            index = st.session_state.index
    
            query_embedding = embedding_model.encode(
                [question]
            )
    
            # Search relevant chunks
            distances, indices = index.search(
                np.array(query_embedding),
                k=5
            )
    
            context = ""
    
            for idx in indices[0]:
                context += chunks[idx]
                context += "\n\n"  
     
            # Ask Gemini
        
            try:
                prompt = f"""
                You are an AI research assistant.
            
                Use ONLY the context below to answer.
            
                Context:
                {context}
            
                Question:
                {question}
            
                Give a clear academic answer.
                """
            
                response = client.models.generate_content(
                    model=MODEL_NAME,
                    contents=prompt
                )
            
                st.subheader("Answer")
                st.write(response.text)
            
            except Exception as e:
            
                if "RESOURCE_EXHAUSTED" in str(e):
                    st.error(
                        "Gemini quota exceeded. Please wait a few minutes and try again."
                    )
                else:
                    st.error(str(e))

    # -----------------------------
    # Paper Insights
    # -----------------------------
    
    if st.button("📊 Paper Insights"):
    
        with st.spinner("Analyzing paper..."):
    
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=f"""
                Analyze this research paper and provide:
    
                Title
                Research Domain
                Research Objective
                Dataset Used
                Methodology
                Key Results
                Contributions
                Limitations
                Future Work
    
                Paper:
    
                {text[:15000]}
                """
            )
    
        st.subheader("📊 Paper Insights")
    
        st.markdown(response.text)
    
        st.download_button(
            "⬇️ Download Paper Insights",
            response.text,
            file_name="paper_insights.txt",
            mime="text/plain"
        )
        
    # -----------------------------
    # Literature Survey Generator
    # -----------------------------

    if st.button("📚 Generate Literature Survey"):
    
        with st.spinner("Generating Literature Survey..."):
    
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=f"""
                Act as an academic research analyst.
            
                Generate a literature survey of the given paper in paragraph format.
            
                Include:
            
                - Research Objective
                - Methodology
                - Dataset Used (if available)
                - Results
                - Contributions
                - Limitations
                - Future Work
            
                Write in a style suitable for a B.Tech/M.Tech literature review chapter.
            
                Use formal academic language.
            
                Paper:
            
                {text[:15000]}
                """
            )
    
            st.subheader("📚 Literature Survey")
        
            st.markdown(response.text)
             
            st.download_button(
            "⬇️ Download Literature Survey",
            response.text,
            file_name="literature_survey.txt",
            mime="text/plain"
            )

    # -----------------------------
    # Research Gap Detector
    # -----------------------------

    if st.button("🔍 Find Research Gaps"):
    
        with st.spinner("Analyzing paper..."):
    
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=f"""
                Act as a research expert.
    
                Analyze the following research paper and identify:
    
                1. Research Gaps
                2. Limitations of the Proposed Method
                3. Unsolved Problems
                4. Future Research Directions
                5. Potential Project Ideas based on this paper
    
                Write in a clear academic format.
    
                Paper:
    
                {text[:15000]}
                """
            )
    
            st.subheader("🔍 Research Gap Analysis")
            
            st.markdown(response.text)
                
            st.download_button(
                "⬇️ Download Research Gap Analysis",
                response.text,
                file_name="research_gap_analysis.txt",
                mime="text/plain"
            )