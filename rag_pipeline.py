#!/usr/bin/env python3
"""
RAG answer generation pipeline.
Learn: semantic search, LLM prompting, web UI
"""

import chromadb
import json
from datetime import datetime
from pathlib import Path
from sentence_transformers import SentenceTransformer

def semantic_search(collection, model, query: str, top_k: int = 3) -> list:
	"""
	Retrieve top-k most similar chunks for a query.

	Args:
	   collection: ChromaDB collection
	   model: Sentence transformer model
	   query: User question
	   top_k: Number of chunks to retrieve

	Returns:
	   List of (chunk_text, metadata, similarity_score) tuples
	"""

	query_embedding = model.encode(query).tolist()

	results = collection.query(
		query_embeddings = [query_embedding],
		n_results = top_k
	)

	retrieved_chunks = []

	if results['documents']:
		for doc, meta, distance in zip(
	        results['documents'][0],
        	results['metadatas'][0],
        	results['distances'][0]
    	):
			similarity = 1 - distance
			retrieved_chunks.append({
        		'text': doc,
        		'source': meta['source'],
        		'section': meta['section'],
        		'similarity': similarity
        	})
	
	return retrieved_chunks

def build_rag_prompt(query: str, retrieved_chunks: list) -> str:
	"""
	Build a RAG prompt that instructs the LLM to:
	- Use only retrieved context
	- Cite sources with [Source N] format
	- Not make up information
	"""

	context = ""

	for i, chunk in enumerate(retrieved_chunks, 1):
		context += f"\n[Source {i}] {chunk['source']} - {chunk['section']}\n"
		context += f"{chunk['text']}\n"
		context += "-" * 70 + "\n"

	prompt = f"""You are a helful assistant answering questions about FastAPI documentation.
	Use ONLY the provided context to answer the question. If the answer is not in the context, say "I don't have enough information."
	IMPORTANT: Cite sources using [Source N] format wherever you use information from the context

	---
	RETRIEVED CONTEXT:
	{context}

	---
	QUESTION: {query}

	ANSWER:"""
	
	return prompt

def generate_answer(query: str, retrieved_chunks: list) -> str:
	"""
	Generate answer using OpenAI API.
	
	Args:
	   query: User question
	   retrieved_chunks: Retrieved context chunks

	Returns:
	   Generated answer with citations
	"""

	prompt = build_rag_prompt(query, retrieved_chunks)

	import ollama

	response = ollama.generate(
		model="llama3.2:3b",
		prompt=prompt,
		stream=False,	)

	return response['response']

def init_rag_components():
	"""
	Initialise ChromaDB and model for Streamlit."""

	client = chromadb.PersistentClient(path='./chromadb')
	collection = client.get_collection('fastapi_docs')

	model = SentenceTransformer('all-MiniLM-L6-v2')

	return collection, model

def log_interaction(question: str, retrieved_chunks: list, answer: str, log_file: Path = Path('./logs/interactions.jsonl')):
	"""
	Log each RAG interaction to a JSONL file.
	
	Args:
	   question: User question
	   retrieved_chunks: List of retrieved chunks
	   answer: Generated answer
	   log_file: Path to JSONL log file
	"""

	log_file.parent.mkdir(exist_ok=True)

	log_entry = {
		'timestamp': datetime.now().isoformat(),
		'question': question,
		'retrieved_sources': [
			{
				'source': chunk['source'],
				'section': chunk['section'],
				'similarity': round(chunk['similarity'], 3)
			}
			for chunk in retrieved_chunks
		],
		'answer' : answer
	}

	with open(log_file, 'a') as f:
		f.write(json.dumps(log_entry) + '\n')

	print(f"Logged interaction to {log_file}")

if __name__ == '__main__':
	import os
	client = chromadb.PersistentClient(path='./chromadb')
	collection = client.get_collection('fastapi_docs')

	model = SentenceTransformer('all-MiniLM-L6-v2')
	
	query = "How do I install FastAPI?"
	chunks = semantic_search(collection, model, query, top_k=3)

	print(f"Query: {query}\n")
	print(f"Retrieved {len(chunks)} chunks:\n")

	answer = generate_answer(query, chunks)

	print("\n" + "=" * 80 + "\n")
	print("ANSWER:\n")
	print("=" * 80 + "\n")
	print(answer)

	log_interaction(query, chunks, answer)
