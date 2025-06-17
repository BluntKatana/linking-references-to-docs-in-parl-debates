import elasticsearch
from config import VECTOR_DB_INDEX
from elasticsearch import Elasticsearch

es = Elasticsearch("http://localhost:9200")

def document_exists(document_id):
    """
    Checks if a document with the given ID exists in the Elasticsearch index.
    """
    try:
        if not document_id.startswith('kst-'):
            document_id = f'kst-{document_id}'
        return es.exists(index=VECTOR_DB_INDEX, id=document_id)
    except Exception as e:
        print(f"Error checking existence for document ID {document_id}: {e}")
        return False # Assume it doesn't exist on error

# Function to index a single document
def index_single_document(document):
    """
    Indexes a single document into Elasticsearch.
    """
    try:
        response = es.index(
            index=VECTOR_DB_INDEX,
            id=document["id"],
            document={
                "id": document["id"],
                "date": document["date"],
                "type": document["type"],
                "title": document["title"],
                "title_embedding": document["title_embedding"],
                "content": document["content"],
                "content_embedding": document["content_embedding"],
            }
        )
    except elasticsearch.exceptions.RequestError as e:
         print(f"Error indexing document {document['id']}: {e.info['error']['type']} - {e.info['error']['reason']}")
         print(e)
    except Exception as e:
        print(f"An unexpected error occurred while indexing document {document['id']}: {e}")
        print(e)

def setup_elasticsearch(dangerously_overwrite_existing_index=False):
    """
    Set up Elasticsearch with the correct index and mappings for vector search.
    """
    # Initialize Elasticsearch client
    es = Elasticsearch('http://localhost:9200')
    es.ping()

    # Delete index if it exists
    if dangerously_overwrite_existing_index:
        if es.indices.exists(index=VECTOR_DB_INDEX):
            print(f"[INFO][setup_elasticsearch] deleting existing index: {VECTOR_DB_INDEX}")
            es.indices.delete(index=VECTOR_DB_INDEX)

    # Create index with mapping
    index_mapping = {
        "mappings": {
            "properties": {
                "id": {"type": "keyword"},
                "date": {"type": "date"},
                "type": {"type": "keyword"},
                "title": {"type": "text"},
                "title_embedding": {
                    "type": "dense_vector",
                    "dims": 768,
                    "index": False,
                },
                "content": {"type": "text"},
                "content_embedding": {
                    "type": "dense_vector",
                    "dims": 768,
                    "index": False,
                },
            }
        },
        "settings": {
            "index": {
                "number_of_shards": 1,
                "number_of_replicas": 0
            }
        }
    }

    if es.indices.exists(index=VECTOR_DB_INDEX):
        print(f"[INFO][setup_elasticsearch] index {VECTOR_DB_INDEX} already exists, not creating a new one.")
    else:
        print(f"[INFO][setup_elasticsearch] creating index: {VECTOR_DB_INDEX}")
        es.indices.create(index=VECTOR_DB_INDEX, body=index_mapping)