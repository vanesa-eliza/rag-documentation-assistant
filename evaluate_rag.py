#!/usr/bin/env python3
"""
Evaluate RAG system on a test set.
Learn: evaluation metrics, SourceHitRate@k, quality assessment
"""

import json
from pathlib import Path
from rag_pipeline import semantic_search, init_rag_components

TEST_QUESTIONS = [
    {
        'question': 'How do I install FastAPI?',
        'expected_sources': ['tutorial', 'installation', 'first_steps']
    },
    {
        'question': 'What is dependency injection in FastAPI?',
        'expected_sources': ['dependencies', 'tutorial']
    },
    {
        'question': 'How do I handle errors in FastAPI?',
        'expected_sources': ['error_handling', 'exceptions']
    },
    {
        'question': 'How do I create a path parameter?',
        'expected_sources': ['path_parameters', 'tutorial']
    },
    {
        'question': 'What are WebSockets in FastAPI?',
        'expected_sources': ['websockets', 'advanced']
    },
    {
        'question': 'How do I add authentication?',
        'expected_sources': ['security', 'authentication', 'oauth2']
    },
    {
        'question': 'How do I return a custom response?',
        'expected_sources': ['responses', 'custom']
    },
    {
        'question': 'What is CORS and how do I enable it?',
        'expected_sources': ['cors', 'security', 'middleware']
    },
    {
        'question': 'How do I use a dataabase with FastAPI?',
        'expected_sources': ['database', 'sql', 'tutorial']
    },
    {
        'question': 'How do I deploy a FastAPI app?',
        'expected_sources': ['deployment', 'production', 'docker']
    },
    {
        'question': 'How do I create multiple routes?',
        'expected_sources': ['routing', 'bigger-applications', 'apirouter']
    },
    {
        'question': 'What is request validation?',
        'expected_sources': ['validation', 'pydantic', 'body']
    },
    {
        'question': 'How do I use background tasks?',
        'expected_sources': ['background', 'tasks']
    },
    {
        'question': 'How do I test FastAPI endpoints?',
        'expected_sources': ['testing', 'testclient', 'pytest']
    },
    {
        'question': 'What are path operation decorators?',
        'expected_sources': ['path_operation', 'decorator']
    }
]

def evaluate_rag(collection, model, test_questions: list, top_k: int = 3):
    """
    Evaluate RAG system on test questions.

    Calculates:
    - SourceHitRate@k: % of expected sources in top-k retrieved
    """
    
    results = []
    hit_rates = []

    for i, test in enumerate(test_questions, 1):
        question = test['question']
        expected_sources = test['expected_sources']

        retrieved_chunks = semantic_search(collection, model, question, top_k=top_k)

        retrieved_sources = [chunk['source'].lower() for chunk in retrieved_chunks]

        hits = sum(1 for expected in expected_sources
                   if any(expected.lower() in source for source in retrieved_sources))
        hit_rate = hits / len(expected_sources) if expected_sources else 0
        hit_rates.append(hit_rate)

        result = {
            'question_id': i,
            'question': question,
            'expected_sources': expected_sources,
            'retrieved_sources': [chunk['source'] for chunk in retrieved_chunks],
            'similarity_scores': [round(chunk['similarity'], 3) for chunk in retrieved_chunks],
            'hits': hits,
            'hit_rate': round(hit_rate, 3)
        }
        results.append(result)

        status = "Done" if hit_rate == 1.0 else "~" if hit_rate > 0 else "Miss"
        print(f"{status} Q{i}: {question[:50]}... -> Hit Rate: {hit_rate:.1%}\n")

    overall_hit_rate = sum(hit_rates) / len(hit_rates) if hit_rates else 0

    print(f"Overall SourceHitRate@{top_k}: {overall_hit_rate:.1%}")
    print(f"Questions answered perfectly: {sum(1 for h in hit_rates if h == 1.0)} / {len(test_questions)}")
    print(f"Questions answered partially: {sum(1 for h in hit_rates if 0 < h < 1.0)} / {len(test_questions)}")
    print(f"Questions answered incorrectly: {sum(1 for h in hit_rates if h == 0.0)} / {len(test_questions)}")

    output_file = Path("./evaluation_results.jsonl")
    with open(output_file, 'w') as f:
        for result in results:
            f.write(json.dumps(result) + '\n')

    return results, overall_hit_rate

if __name__ == '__main__':
    collection, model = init_rag_components()

    results, hit_rate = evaluate_rag(collection, model, TEST_QUESTIONS, top_k=3)