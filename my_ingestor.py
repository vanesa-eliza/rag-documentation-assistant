	#!/usr/bin/env python3

"""
Document ingestion system
Learn: file handling, text processing, JSON, data structures
"""

import os
import re
import json
from pathlib import Path
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class Chunk:
	"""Represents one chunk of text with metadata."""
	source: str
	section: str
	chunk_index: int
	text: str
	char_count: int
	token_estimate: int

def find_md_files(root_dir: Path) -> List[Path]:
	"""Find all .md files in a directory."""
	files = []

	#Recursively search for .md files
	for md_file in root_dir.rglob('*.md'):
		files.append(md_file)

	return sorted(files)

def read_file(file_path: Path) -> str:
	"""Read md file and return plain text."""
	try:
		content = file_path.read_text(encoding='utf-8', errors = 'ignore')
		return content
	except Exception as e:
		print(f"Error reading {file_path}: {e}")
		return ""

def extract_headers(text: str) -> List[Tuple[str, str]]:
	"""
	Split text by markdown headers (# ## ###).
	Returns: [(headers_title, section_text), ...]
	"""

	header_pattern = r'^(#{1,6})\s+(.+)$'

	lines = text.split('\n')
	sections = []

	current_header = "Untitled"
	current_text = []
	in_code_block = False

	for line in lines:
		if line.strip().startswith('```'):
			in_code_block = not in_code_block
			current_text.append(line)
			continue

		if not in_code_block:
			match = re.match(header_pattern, line)

			if match:
				section_text = '\n'.join(current_text).strip()
				if section_text and len(section_text) > 50:
					sections.append((current_header, section_text))

				full_header = match.group(2).strip()
				header_clean = re.sub(r'\s*\{.*\}$', '', full_header)
				current_header = header_clean
				current_text = []
			else:
				current_text.append(line)
	section_text = '\n'.join(current_text).strip()
	if section_text and len(section_text) > 50:
		sections.append((current_header, section_text))
	
	return sections

def create_chunks(sections: List[Tuple[str, str]], file_path: Path) -> List[Chunk]:
	"""
		Convert sections into chunks.
	
		Strategy:
	- If section < 600 chars: create 1 chunk
	- If section > 600 chars: split by sentences
	"""
	
	chunks = []
	chunk_index = 0

	for header, section_text in sections:
		if len(section_text) < 80:
			continue

		if len(section_text) <= 600:
			chunk = Chunk(
	                	source=str(file_path.relative_to(file_path.parent.parent.parent)),
              			section=header,
               		 	chunk_index=chunk_index,
        	        	text=section_text,
	              		char_count=len(section_text),
                		token_estimate=int(len(section_text) / 4)  # Rough: 1 token ≈ 4 chars
            		)
			chunks.append(chunk)
			chunk_index += 1
		else:
			sentences = re.split(r'(?<=[.!?])\s+', section_text)    
			current_chunk_text = []
			current_size = 0
			part_num = 0
	
			for sentence in sentences:
				if current_size + len(sentence) > 600 and current_chunk_text:
					text = ' '.join(current_chunk_text)
					chunk = Chunk(
						source=str(file_path.relative_to(file_path.parent.parent.parent)),
						section=f"{header} (part {part_num})",
						chunk_index=chunk_index,
						text=text,
						char_count=len(text),
						token_estimate=int(len(text) / 4)
					)
					chunks.append(chunk)
					chunk_index += 1
					part_num += 1
					current_chunk_text = []
					current_size = 0
	
				current_chunk_text.append(sentence)
				current_size += len(sentence)
	
			if current_chunk_text:
				text = ' '.join(current_chunk_text)
				chunk = Chunk(
					source=str(file_path.relative_to(file_path.parent.parent.parent)),
					section=header + (f" (part {part_num})" if part_num > 0 else ""),
					chunk_index=chunk_index,
					text=text,
					char_count=len(text),
					token_estimate=int(len(text) / 4)
				)
				chunks.append(chunk)
				chunk_index += 1
	return chunks
		
def ingest_all(root_dir: Path) -> List[Chunk]:
    
    files = find_md_files(root_dir)
    all_chunks = []
    
    for i, file_path in enumerate(files, 1):
        content = read_file(file_path)
        if not content or len(content) < 50:
            print(f"{file_path.name:45s} (empty, skipped)")
            continue

        sections = extract_headers(content)
        
        chunks = create_chunks(sections, file_path)
        
        if chunks:
            all_chunks.extend(chunks)
            print(f"{file_path.name:45s} → {len(chunks):3d} chunks")
        else:
            print(f"{file_path.name:45s} (0 chunks)")
    
    return all_chunks


def save_chunks_jsonl(chunks: List[Chunk], output_file: Path):
    """Save chunks as JSONL (one per line)."""
    output_file.parent.mkdir(exist_ok=True)
    
    with open(output_file, 'w') as f:
        for chunk in chunks:
            chunk_dict = {
                'source': chunk.source,
                'section': chunk.section,
                'chunk_index': chunk.chunk_index,
                'text': chunk.text,
                'char_count': chunk.char_count,
                'token_estimate': chunk.token_estimate,
            }
            f.write(json.dumps(chunk_dict) + '\n')

def save_stats(chunks: List[Chunk], output_file: Path):
    """Save statistics as JSON."""
    output_file.parent.mkdir(exist_ok=True)
    
    char_counts = [c.char_count for c in chunks]
    token_counts = [c.token_estimate for c in chunks]
    
    stats = {
        'total_chunks': len(chunks),
        'avg_chunk_size_chars': round(sum(char_counts) / len(char_counts), 1) if char_counts else 0,
        'avg_chunk_size_tokens': round(sum(token_counts) / len(token_counts), 1) if token_counts else 0,
        'min_chunk_size': min(char_counts) if char_counts else 0,
        'max_chunk_size': max(char_counts) if char_counts else 0,
        'median_chunk_size': sorted(char_counts)[len(char_counts)//2] if char_counts else 0,
    }
    
    with open(output_file, 'w') as f:
        json.dump(stats, f, indent=2)


if __name__ == '__main__':
	docs_dir = Path('./fastapi/docs/en/docs')
	output_dir = Path('./output')

	chunks = ingest_all(docs_dir)
	
	if chunks:
		avg_size = sum(c.char_count for c in chunks) / len(chunks)
		avg_tokens = sum(c.token_estimate for c in chunks) / len(chunks)
		print(f"   Total chunks: {len(chunks)}")
		print(f"   Avg size: {avg_size:.0f} chars ({avg_tokens:.0f} tokens)")
		print(f"   Min size: {min(c.char_count for c in chunks)} chars")
		print(f"   Max size: {max(c.char_count for c in chunks)} chars")

	save_chunks_jsonl(chunks, output_dir / 'chunks.jsonl')
	save_stats(chunks, output_dir / 'stats.json')
