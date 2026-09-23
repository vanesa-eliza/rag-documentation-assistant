#!/usr/bin/env python3
"""
Embedding generation and ChromaDB indexing.
Learn: sentence embeddings, vector databases, metadata handling
"""

import json
import chromadb
from pathlib import Path
from sentence_transformers import SentenceTransformer

def load_chunks_from_jsonl(jsonl_file: Path) -> list:
	"""Load all chunks from JSONL file."""
	chunks = []

	with open(jsonl_file, 'r') as f:
		for line in f:
			if line.strip():
				chunk = json.loads(line)
				chunks.append(chunk)

	return chunks

def init_chromadb_client(db_dir: Path = None) -> chromadb.Client:
	"""
	Initialise ChromaDB client.
	
	If db_dir is None: use in-memory (ephemeral)
	If db_dir is provided: persist to disk (supports re-runs)
	"""
	
	if db_dir is None:
		return chromadb.EphemeralClient()
	else:
		db_dir.mkdir(exist_ok=True)
		return chromadb.PersistentClient(path=str(db_dir))
	
def load_embedding_model(model_name: str = "all-MiniLM-L6-v2") -> SentenceTransformer:
	"""Load sentence-transformer model.
	
	all-MiniLM-L6-v2:
	- Fast and lightweight
	- 384-dimentional embeddings
	-Good for semantic similarity
	- ~80 MB
	"""
	print(f"Loading model: {model_name}...")
	model = SentenceTransformer(model_name)
	print(f"Model loaded (embedding dimension: {model.get_sentence_embedding_dimension()})")
	
	return model

def get_or_create_collection(client: chromadb.Client, collection_name: str = "fastapi_docs"):
	"""
	Get existing collection or create new one.
	
	Supports full re-runs:
	- If collection exists: gets it (can delete/reset if needed)
	- If not: creates new collection
	"""

	collection = client.get_or_create_collection(
		name=collection_name,
		metadata={"hnsw:space": "cosine"})
	
	return collection

def index_chunks(collection, chunks: list, model, batch_size: int = 50):
	"""
	Generate embeddings and index chunks in ChromaDB.
	
	Args:
		collection: ChromaDB collection
		chunks: List of chunk dictionaries
		model: Sentence transformer model
		batch_size: Process chunks in batches for efficiency
	"""

	total = len(chunks)

	print(f"\nIndexing {total} chunks...")
	
	for i in range(0, total, batch_size):
		batch = chunks[i:i + batch_size]

		ids = []
		documents = []
		embeddings = []
		metadatas = []

		for chunk in batch:
			chunks_id = f"{chunk['source']}_{chunk['chunk_index']}"

			ids.append(chunks_id)
			documents.append(chunk['text'])
			metadatas.append({
				'source': chunk['source'],
				'section': chunk['section'],
				'chunk_index': str(chunk['chunk_index']),
				'char_count': str(chunk['char_count']),
				'token_estimate': str(chunk['token_estimate'])
			})

		embeddings = model.encode(documents).tolist()

		collection.add(
			ids=ids,
			documents=documents,
			embeddings=embeddings,
			metadatas=metadatas
		)

		processed = min(i + batch_size, total)
		print(f"Indexed {processed}/{total} chunks ({100*processed/total:.1f}%)")

	print(f"Successfully indexed {total} chunks\n")

def test_retrieval(collection, model, query: str, n_results: int = 5):
	"""
	Test retrieval with a query.
	Shows top-k similar chunks.
	"""

	query_embedding = model.encode(query).tolist()

	results = collection.query(
		query_embeddings=[query_embedding],
		n_results=n_results
	)

	if results['documents']:
		for i, (doc, meta, dist) in enumerate(zip(
			results['documents'][0],
			results['metadatas'][0],
			results['distances'][0]
		), 1):
			print(f"\n{i}. {meta['source']} - {meta['section']}")
			print(f"  Similarity: {1 - dist:.3f}")
			print(f"  Text: {doc[:150]}...")

if __name__ == '__main__':
	chunks_file = Path('./output/chunks.jsonl')
	db_dir = Path('./chromadb')

	print("Embedding & Indexing Pipeline\n")

	chunks = load_chunks_from_jsonl(chunks_file)

	print(f"Loaded {len(chunks)} chunks")

	client = init_chromadb_client(db_dir)
	collection = get_or_create_collection(client)

	model = load_embedding_model("all-MiniLM-L6-v2")

	index_chunks(collection, chunks, model, batch_size=100)

	print(f"Total chunks in index: {collection.count()}")

	test_queries = [
		"What is FastAPI?",
		"How to define a route in FastAPI?",
		"Explain dependency injection in FastAPI.",
		"How to handle errors in FastAPI?",
		"What are the best practices for FastAPI development?"
	]

	for query in test_queries:
		test_retrieval(collection, model, query, n_results=3)


	print("\n" + "="*70)
	print("Custom query test:")
	print("="*70)
	test_retrieval(collection, model, "How do I upload files?", n_results=3)
