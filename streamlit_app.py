#!/usr/bin/env python3
"""
RAG Streamlit interface for FastAPI documentation Q&A.
"""

import streamlit as st
from rag_pipeline import semantic_search, generate_answer, init_rag_components, log_interaction
from pathlib import Path

st.set_page_config(
	page_title="FastAPI RAG Assistant",
	page_icon="🚀",
	layout="wide"
)

st.title("FastAPI Documentation Assistant")
st.markdown("Ask questions about FastAPI and get answers from the official documentation.")

with st.sidebar:
	st.header("⚙️ Settings")
	top_k = st.slider("Number of chunks to retrieve", 1, 20, 15)

@st.cache_resource
def load_components():
	return init_rag_components()

collection, model = load_components()

st.markdown("---")

question = st.text_input("Ask a question about FastAPI:")

if question:
	with st.spinner("Searching and generating answer..."):
		retrieved_chunks = semantic_search(collection, model, question, top_k=top_k)
		
		answer = generate_answer(question, retrieved_chunks)

		log_interaction(question, retrieved_chunks, answer)

		st.markdown("### Answer")
		st.markdown(answer)

		st.markdown("### Sources")
		for i, chunk in enumerate(retrieved_chunks, 1):
			with st.container():
				st.markdown(f"**[Source {i}]** {chunk['source']}")
				st.markdown(f"*{chunk['section']}* | Similarity: {chunk['similarity']:.1%}")

		with st.expander("View Retrieved Context"):
			for i, chunk in enumerate(retrieved_chunks, 1):
				st.markdown(f"### Source {i}")
				st.markdown(f"**File:** `{chunk['source']}`")
				st.markdown(f"**Section:** {chunk['section']}")
				st.markdown(f"**Similarity:** {chunk['similarity']:.3f}")
				st.markdown("**Text:**")
				st.markdown(chunk['text'])
				st.markdown("---")
