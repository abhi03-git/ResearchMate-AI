from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import faiss
import numpy as np
import streamlit as st
from pypdf import PdfReader
from openai import OpenAI
from dotenv import load_dotenv
import os

#load .env
load_dotenv()

# Check if API key is loaded
if not os.getenv("OPENROUTER_API_KEY"):
    st.error("❌ OPENROUTER_API_KEY not found in .env")
    st.stop()

# Openai API Key
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

MODEL_NAME = "openai/gpt-oss-20b:free"

def download_result(button_text, content, filename):
    st.download_button(
        label=button_text,
        data=content,
        file_name=filename,
        mime="text/plain"
    )

# Sidebar
with st.sidebar:

    st.markdown("# 📚 ResearchMate AI")

    st.markdown("---")

    st.markdown("### 🤖 AI Research Assistant")

    st.markdown("""
    Analyze research papers using:

    - 🧠 AI Summarization
    - 📚 Literature Review
    - 🔍 Research Gap Detection
    - 💬 RAG-based Chat
    - 📊 Paper Analytics
    - 🚀 Proposal Generation
    """)

    st.markdown("---")

    st.markdown("### ⚙️ Settings")

    model_choice = st.selectbox(
        "Choose Model",
        [
            "GPT OSS 20B"
        ]
    )

    st.markdown("---")

    st.markdown(
        """
        <div style='text-align:center'>
        <small>
        ResearchMate AI v1.0
        </small>
        </div>
        """,
        unsafe_allow_html=True
    )

#Title
st.title("📚 ResearchMate AI")
st.markdown("""
<style>

.main {
    padding-top: 1rem;
}

.stButton button {
    width: 100%;
    border-radius: 10px;
    height: 3em;
    font-weight: 600;
}

.stDownloadButton button {
    width: 100%;
    border-radius: 10px;
}

div[data-testid="metric-container"] {
    background: linear-gradient(
        135deg,
        #1e293b,
        #0f172a
    );
    border: 1px solid #334155;
    padding: 18px;
    border-radius: 16px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.25);
}

</style>
""", unsafe_allow_html=True)

st.info(
    """
    💡 Ask questions about your uploaded papers.

    Examples:

    • What is the main contribution?

    • What dataset was used?

    • What are the limitations?

    • Suggest future work.
    """
)

#Chat History
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

uploaded_files = st.file_uploader(
    "Upload Research Papers",
    type=["pdf"],
    accept_multiple_files=True
)

if uploaded_files:
    st.markdown("""
    # 🧠 ResearchMate AI
    
    ### Your Intelligent Research Companion
    
    Upload research papers and instantly:
    
    ✅ Generate summaries
    
    ✅ Detect research gaps
    
    ✅ Create literature surveys
    
    ✅ Compare papers
    
    ✅ Chat with PDFs
    
    ✅ Generate proposals
    
    """)
    
    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "📄 Summarize",
            "💬 AI Chat",
            "📊 Analytics",
            "🚀 Research Lab"
        ]
    )

    papers = []
    text = ""
    
    for uploaded_file in uploaded_files:
    
        reader = PdfReader(uploaded_file)
    
        paper_text = ""
    
        for page in reader.pages:
    
            page_text = page.extract_text()
    
            if page_text:
                paper_text += page_text
    
        papers.append(
            {
                "name": uploaded_file.name,
                "content": paper_text
            }
        )
    
        text += paper_text
    
    st.session_state.papers = papers

    # paper count display
    st.toast(
        f"✅ {len(uploaded_files)} paper(s) loaded successfully!"
    )

    #Uploading papers
    st.subheader("Uploaded Papers")

    for file in uploaded_files:
        st.write("📄", file.name)

    st.markdown("### 📄 Paper Preview")

    with st.container():
        st.write(text[:3000])
    
    st.divider()
        
    # Process paper only once
    current_file_count = len(uploaded_files)
    
    if (
        "processed" not in st.session_state
        or st.session_state.get("file_count") != current_file_count
    ):
    
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
        st.session_state.file_count = current_file_count
        
    # -----------------------------
    # Research Dashboard
    # -----------------------------
    
    st.markdown("## 📊 Research Dashboard")
    
    total_pages = sum(
        len(PdfReader(file).pages)
        for file in uploaded_files
    )
    
    total_chunks = len(
        st.session_state.get("chunks", [])
    )
    
    total_chats = len(
        st.session_state.chat_history
    )

    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📄 Papers",
            value=len(uploaded_files)
        )
    
    with col2:
        st.metric(
            label="📑 Pages",
            value=total_pages
        )
    
    with col3:
        st.metric(
            label="🧩 Chunks",
            value=total_chunks
        )
    
    with col4:
        st.metric(
            label="💬 Chats",
            value=total_chats
        )

    with tab1:

        if st.button("Generate Summary"):
    
            with st.spinner("Generating summary..."):
                
                prompt = f"""
                Summarize this research paper:
    
                {text[:12000]}
                """
                
                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                )
    
                answer = response.choices[0].message.content
            st.toast("✅ Summary generated successfully")
            st.subheader("Summary")
            st.write(answer)
    
            st.download_button(
                "⬇️ Download Summary",
                answer,
                file_name="paper_summary.txt",
                mime="text/plain"
            )                      
        # -----------------------------
        # Abstract Generator
        # -----------------------------
    
        if st.button("📝 Generate Abstract"):
    
            with st.spinner("Generating abstract..."):
        
                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[
                        {
                            "role": "user",
                            "content": f"""
                            Create a professional research paper abstract
                            from the following content.
        
                            Paper:
        
                            {text[:15000]}
                            """
                        }
                    ]
                )
        
                answer = response.choices[0].message.content
        
                st.subheader("📝 Abstract")
                st.markdown(answer)
                st.download_button(
                    "⬇️ Download Abstract",
                    answer,
                    file_name="abstract.txt",
                    mime="text/plain"
                )

    with tab2:

        st.subheader("💬 AI Research Chat")
    
        st.caption(
            "Ask questions about the uploaded research papers."
        )

        # Chat Statistics
    
        chat_count = len(
            st.session_state.chat_history
        )
    
        st.metric(
            "💬 Total Conversations",
            chat_count
        )
    
        # Suggested Questions

        st.info(
            """
            💡 Suggested Questions
        
            • What is the main contribution?
        
            • What dataset was used?
        
            • What are the limitations?
        
            • Compare methodologies.
        
            • Suggest future research directions.
        
            • Summarize the findings.
            """
        )
    
        # Display Chat History First
    
        for chat in st.session_state.chat_history:
    
            with st.chat_message("user"):
                st.write(chat["question"])
    
            with st.chat_message("assistant"):
                st.write(chat["answer"])

        # Chat Input
    
        question = st.chat_input(
            "Ask anything about the uploaded research papers..."
        )
    
        if question:
    
            # Show User Message
    
            with st.chat_message("user"):
                st.write(question)
    
            with st.spinner("Searching research papers..."):
    
                chunks = st.session_state.chunks
    
                embedding_model = st.session_state.embedding_model
    
                index = st.session_state.index
    
                query_embedding = embedding_model.encode(
                    [question]
                )
    
                distances, indices = index.search(
                    np.array(query_embedding),
                    k=5
                )
    
                context = ""
    
                for idx in indices[0]:
    
                    context += chunks[idx]
                    context += "\n\n"
    
                try:
    
                    prompt = f"""
                    You are ResearchMate AI.
    
                    Answer ONLY from the provided context.
    
                    Context:
                    {context}
    
                    Question:
                    {question}
    
                    Give a clear academic answer.
                    """
    
                    response = client.chat.completions.create(
                        model=MODEL_NAME,
                        messages=[
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ]
                    )
    
                    answer = response.choices[0].message.content
    
                    # Show Assistant Response
    
                    with st.chat_message("assistant"):
                        st.write(answer)
    
                    # Save History
    
                    st.session_state.chat_history.append(
                        {
                            "question": question,
                            "answer": answer
                        }
                    )
    
                    st.toast(
                        "✅ Answer generated"
                    )
    
                except Exception as e:
    
                    st.error(str(e))

        # -----------------------------
        # Chat Controls
        # -----------------------------
    
        col1, col2 = st.columns(2)
    
        with col1:
    
            if st.button("🗑️ Clear Chat History"):
    
                st.session_state.chat_history = []
    
                st.rerun()
    
        with col2:
    
            if st.button("📥 Download Chat History"):
    
                chat_text = ""
    
                for chat in st.session_state.chat_history:
    
                    chat_text += (
                        f"Question: {chat['question']}\n\n"
                    )
    
                    chat_text += (
                        f"Answer: {chat['answer']}\n\n"
                    )
    
                    chat_text += (
                        "-" * 50 + "\n\n"
                    )
    
                st.download_button(
                    "⬇️ Save Chat",
                    chat_text,
                    file_name="chat_history.txt",
                    mime="text/plain"
                )

    # -----------------------------
    # Paper Insights
    # -----------------------------

    with tab3:
        if st.button("📊 Paper Insights"):
    
            with st.spinner("Analyzing paper..."):
        
                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[
                        {
                            "role": "user",
                            "content": f"""
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
                        }
                    ]
                )
        
            answer = response.choices[0].message.content
            
            st.subheader("📊 Paper Insights")
            
            st.markdown(answer)
        
            st.download_button(
                "⬇️ Download Paper Insights",
                answer,
                file_name="paper_insights.txt",
                mime="text/plain"
            )
        
        # -----------------------------
        # Literature Matrix Generator
        # -----------------------------
    
        if st.button("📚 Generate Literature Matrix"):
        
            with st.spinner("Generating Literature Matrix..."):
                
                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[
                        {
                            "role": "user",
                            "content" : f"""
                            Act as a research analyst.
                            
                            Create a literature matrix table from the uploaded papers.
                            
                            Columns:
                            
                            - Research Objective
                            - Methodology
                            - Dataset
                            - Key Results
                            - Limitations
                            - Future Work
                            
                            Return the result as a Markdown table.
                            
                            Paper Content:
                            
                            {text[:20000]}
                            """
                        }
                    ]
                )
                
                answer = response.choices[0].message.content
                
                st.subheader("📚 Literature Matrix")
                st.markdown(answer)
                 
                st.download_button(
                    "⬇️ Download Literature Matrix",
                    answer,
                    file_name="literature_Matrix.txt",
                    mime="text/plain"
                )


        # -----------------------------
        # Literature Survey Generator
        # -----------------------------
    
        if st.button("📚 Generate Literature Survey"):
    
            with st.spinner("Generating Literature Survey..."):
        
                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[
                        {
                            "role": "user",
                            "content": f"""
                            Generate a detailed literature survey.
        
                            For every important study:
        
                            - Author
                            - Objective
                            - Methodology
                            - Dataset
                            - Results
                            - Limitations
        
                            Write in academic style.
        
                            Paper:
        
                            {text[:20000]}
                            """
                        }
                    ]
                )
        
                answer = response.choices[0].message.content
            st.toast("📚 Literature survey generated")
            st.subheader("📚 Literature Survey")
        
            st.markdown(answer)
        
            st.download_button(
                "⬇️ Download Literature Survey",
                answer,
                file_name="literature_survey.txt",
                mime="text/plain"
            )
    
        # -----------------------------
        # Paper comparison 
        # -----------------------------

        if st.button("⚖️ Compare Papers"):

            if len(uploaded_files) < 2:
        
                st.warning(
                    "Please upload at least 2 research papers for comparison."
                )

            else:
        
                with st.spinner("Comparing papers..."):
        
                    paper_context = ""
        
                    for i, paper in enumerate(papers):
        
                        paper_context += f"""
        
                        PAPER {i+1}
        
                        File Name: {paper['name']}
        
                        Content:
        
                        {paper['content'][:8000]}
        
                        """
        
                    response = client.chat.completions.create(
                        model=MODEL_NAME,
                        messages=[
                            {
                                "role": "user",
                                "content": f"""
                                Compare the following research papers.
        
                                For EACH paper identify:
        
                                1. Research Objective
                                2. Methodology
                                3. Dataset
                                4. Key Results
                                5. Limitations
                                6. Future Work
        
                                Return the comparison as a Markdown table.
        
                                {paper_context}
                                """
                            }
                        ]
                    )
        
                    answer = response.choices[0].message.content
        
                    st.subheader("⚖️ Paper Comparison")
        
                    st.markdown(answer)
        
                    st.download_button(
                        "⬇️ Download Paper Comparison",
                        answer,
                        file_name="paper_comparison.txt",
                        mime="text/plain"
                    )
        
    # -----------------------------
    # Research Gap Detector
    # -----------------------------
    with tab4:
        if st.button("🔍 Find Research Gaps"):
    
            with st.spinner("Analyzing paper..."):
        
                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[
                        {
                            "role": "user",
                            "content": f"""
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
                        }
                    ]
                )
                
                answer = response.choices[0].message.content
            st.toast("🔍 Research gaps identified")
            st.subheader("🔍 Research Gap Analysis")
                
            st.markdown(answer)
                    
            st.download_button(
                "⬇️ Download Research Gap Analysis",
                answer,
                file_name="research_gap_analysis.txt",
                mime="text/plain"
            )

        # -----------------------------
        # Citation Generator
        # -----------------------------
    
        if st.button("📖 Generate Citations"):
           with st.spinner("Generating citations..."):
    
                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[
                        {
                            "role": "user",
                            "content": f"""
                            Generate citations for the uploaded research papers.
        
                            Provide:
                            1. APA Style
                            2. IEEE Style
                            3. MLA Style
        
                            Paper Content:
        
                            {text[:15000]}
                            """
                        }
                    ]
                )
        
                answer = response.choices[0].message.content
        
                st.subheader("📖 Generated Citations")
                st.markdown(answer)
                st.download_button(
                    "⬇️ Download Citations",
                    answer,
                    file_name="citations.txt",
                    mime="text/plain"
                )

 
        # -----------------------------
        # Research Questions Generator
        # -----------------------------
    
        if st.button("❓ Generate Research Questions"):
    
            with st.spinner("Generating research questions..."):
        
                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[
                        {
                            "role": "user",
                            "content": f"""
                            Based on the paper, generate:
        
                            - 10 Research Questions
                            - 5 Advanced Research Questions
                            - 5 Potential Thesis Topics
        
                            Paper:
        
                            {text[:15000]}
                            """
                        }
                    ]
                )
        
                answer = response.choices[0].message.content
        
                st.subheader("❓ Research Questions")
                st.markdown(answer)
                st.download_button(
                    "⬇️ Download Research Questions",
                    answer,
                    file_name="research_questions.txt",
                    mime="text/plain"
                )
        
        # -----------------------------
        # Methodology Extractor
        # -----------------------------
    
        if st.button("⚙️ Extract Methodology"):
    
            with st.spinner("Extracting methodology..."):
    
                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[
                        {
                            "role": "user",
                            "content": f"""
                            Extract the methodology section.
        
                            Include:
        
                            - Research Design
                            - Dataset
                            - Algorithms Used
                            - Experimental Setup
                            - Evaluation Metrics
        
                            Paper:
        
                            {text[:15000]}
                            """
                        }
                    ]
                )
        
                answer = response.choices[0].message.content
        
                st.subheader("⚙️ Methodology")
                st.markdown(answer)
                st.download_button(
                    "⬇️ Download Methodology",
                    answer,
                    file_name="methodology.txt",
                    mime="text/plain"
                )
            
        # -----------------------------
        # Research Proposal Generator
        # -----------------------------
    
        if st.button("🚀 Generate Research Proposal"):
    
            with st.spinner("Generating proposal..."):
        
                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[
                        {
                            "role": "user",
                            "content": f"""
                            Based on this research paper create a new
                            research proposal.
        
                            Include:
        
                            1. Title
                            2. Problem Statement
                            3. Objectives
                            4. Proposed Methodology
                            5. Expected Outcomes
                            6. Future Scope
        
                            Paper:
        
                            {text[:15000]}
                            """
                        }
                    ]
                )
        
                answer = response.choices[0].message.content
            st.toast("🚀 Research proposal created")
            st.subheader("🚀 Research Proposal")
            st.markdown(answer)
            st.download_button(
                "⬇️ Download Research Proposal",
                answer,
                file_name="research_proposal.txt",
                mime="text/plain"
            )
                
        # -----------------------------
        # Keyword Extraction
        # -----------------------------  
    
        if st.button("🔑 Extract Keywords"):
    
            with st.spinner("Extracting keywords..."):
        
                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[
                        {
                            "role": "user",
                            "content": f"""
                            Extract:
        
                            - 20 Important Keywords
                            - Technical Terms
                            - Research Concepts
                            - AI/ML Techniques (if any)
        
                            Paper:
        
                            {text[:15000]}
                            """
                        }
                    ]
                )
        
                answer = response.choices[0].message.content
        
                st.subheader("🔑 Keywords")
                st.markdown(answer)
                st.download_button(
                    "⬇️ Download Keywords",
                    answer,
                    file_name="keywords.txt",
                    mime="text/plain"
                )
    
        # -----------------------------
        # Research Trend Analyzer
        # ----------------------------- 
    
        if st.button("📈 Research Trend Analysis"):
    
            with st.spinner("Analyzing trends..."):
        
                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[
                        {
                            "role": "user",
                            "content": f"""
                            Analyze this paper and identify:
        
                            - Popular Keywords
                            - Research Trends
                            - Common Techniques
                            - Popular Datasets
                            - Emerging Topics
        
                            Paper:
        
                            {text[:15000]}
                            """
                        }
                    ]
                )
        
                answer = response.choices[0].message.content
        
                st.subheader("📈 Research Trend Analysis")
        
                st.markdown(answer)
        
                st.download_button(
                    "⬇️ Download Trend Analysis",
                    answer,
                    file_name="trend_analysis.txt",
                    mime="text/plain"
                )
    
        # -----------------------------
        # Topic Recommendation Engine
        # -----------------------------   
    
        if st.button("📚 Recommend Related Topics"):
    
            with st.spinner("Finding related topics..."):
        
                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[
                        {
                            "role": "user",
                            "content": f"""
                            Based on the uploaded paper suggest:
        
                            - Related Research Areas
                            - Emerging Research Topics
                            - Future Research Directions
                            - Project Ideas
                            - Survey Paper Ideas
        
                            Paper:
        
                            {text[:15000]}
                            """
                        }
                    ]
                )
        
                answer = response.choices[0].message.content
        
                st.subheader("📚 Related Topics")
                st.markdown(answer)
                st.download_button(
                    "⬇️ Download Topic Recommendations",
                    answer,
                    file_name="topic_recommendations.txt",
                    mime="text/plain"
                )

    # -----------------------------
    # Footer
    # -----------------------------
        
    st.markdown("---")

    st.markdown(
        """
        <div style='text-align:center'>
        
        <h4>📚 ResearchMate AI</h4>
        
        AI-powered Research Assistant
        
        Built with Streamlit • OpenRouter • FAISS • Sentence Transformers
        
        </div>
        """,
        unsafe_allow_html=True
    )