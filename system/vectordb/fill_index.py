

# Updated process_batch function for immediate indexing and existence check
import argparse
import os
import sys

from system.config import OUTPUT_DIR

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
import requests
from tqdm import tqdm

from utils.obm import get_obm_html
from utils.parse import html_to_md
from vectordb.crud import document_exists, index_single_document
from vectordb.embedder import embedding


def process_batch(input_path):
    df = pd.read_csv(input_path)
    indexed_count = 0
    skipped_count = 0

    for _, row in tqdm(df.iterrows(), total=len(df), desc="Processing documents"):
        try:
            document_id = row['identifier']
            document_type = row['type']
            document_title = row['title']
            document_date = row['date']

            if document_type != 'dossier':
                # Check if the document already exists in the index
                if document_exists(document_id):
                    skipped_count += 1
                    # tqdm.write(f"Skipping document {document_id} ({document_type}): Already exists in index.")
                    continue # Skip to the next document

                # If document doesn't exist, proceed with processing and embedding
                html_content = get_obm_html(document_id)

                vector_info = {
                    'id': document_id,
                    'title': document_title,
                    'date': document_date,
                    'content': html_to_md(html_content),
                }

                if vector_info is None:
                    tqdm.write(f"Skipping document {document_id} ({document_type}): Failed to retrieve information.")
                    continue
                vector_info['type'] = document_type

                # Generate embedding using the document content and the Retriever
                title_text = vector_info.get('title', '') or ''
                content_text = vector_info.get('content', '') or ''

                title_embedding = None
                content_embedding = None

                if title_text:
                    try:
                        title_embedding = embedding.dense_encode(title_text)
                    except Exception as e:
                        tqdm.write(f"Error generating title embedding for {document_id}: {e}")
                        title_embedding = None

                if content_text:
                    try:
                        content_embedding = embedding.dense_encode(content_text)
                    except Exception as e:
                        tqdm.write(f"Error generating content embedding for {document_id}: {e}")
                        content_embedding = None

                # Only index if both embeddings were generated successfully
                if title_embedding is not None and content_embedding is not None:
                    vector_info["title_embedding"] = title_embedding
                    vector_info['content_embedding'] = content_embedding

                    # Index the single document immediately
                    index_single_document(vector_info)
                    indexed_count += 1
                else:
                    tqdm.write(f"Skipping indexing for document {document_id} due to embedding failure.")
        except requests.exceptions.RequestException as e:
            tqdm.write(f"Error retrieving document {document_id} ({document_type}): {e}")
            continue  # Skip to the next document
        except Exception as e:
            tqdm.write(f"Unexpected error processing document {document_id} ({document_type}): {e}")
            continue  # Skip to the next document


    print(f"\nProcessing finished.")
    print(f"Total documents processed: {len(df)}")
    print(f"Documents indexed: {indexed_count}")
    print(f"Documents skipped (already in index): {skipped_count}")


if __name__ == "__main__":
    """
    Fill the vector database with documents and dossiers from a CSV file.

    The csv file should contain the following columns:
    - identifier: The unique identifier for the document.
    - type: The type of the document (e.g., 'document', 'dossier').
    - title: The title of the document.
    - date: The date of the document.

    Example usage:
        # Run the script relative to the system directory (to ensure correct imports)
        python -m system.vectordb.fill_index -i ./system/data/documents_annotated_batch.csv
    """
    parser = argparse.ArgumentParser(description="Extract documents and dossiers from a CSV file.")
    parser.add_argument("-i", "--input_path", help="Path to the CSV file containing identifiers.", required=True)

    args = parser.parse_args()
    process_batch(args.input_path)