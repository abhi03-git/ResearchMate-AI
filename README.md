# ResearchMate AI

ResearchMate AI is an AI-powered research assistant built using Streamlit, Google Gemini API, FAISS, and Sentence Transformers. The application helps researchers, students, and academicians analyze research papers efficiently.

## Features

* Upload PDF research papers
* Generate concise paper summaries
* Generate detailed literature surveys
* Identify research gaps and future work opportunities
* Extract key paper insights
* Chat with research papers using AI-powered semantic search
* Download generated outputs

## Tech Stack

* Python
* Streamlit
* Google Gemini API
* Sentence Transformers
* FAISS
* LangChain Text Splitters
* PyPDF
* NumPy

## Project Architecture

1. Upload PDF Research Paper
2. Extract Text using PyPDF
3. Split Text into Chunks
4. Generate Embeddings using Sentence Transformers
5. Store Embeddings in FAISS Vector Database
6. Retrieve Relevant Context
7. Generate Responses using Gemini API

## Installation

```bash
pip install -r requirements.txt
```

## Run the Application

```bash
streamlit run app.py
```

## Features Implemented

* Research Paper Summarization
* Literature Survey Generation
* Research Gap Detection
* Paper Insights Extraction
* RAG-based Question Answering

## Future Enhancements

* Multi-PDF Comparison
* Citation Generation
* PDF Report Export
* Research Recommendation Engine
* Academic Knowledge Graph

## Author

Abhishek Banala

B.Tech - Computer Science and Engineering (AI & ML)

Malla Reddy Engineering College and Management Sciences
