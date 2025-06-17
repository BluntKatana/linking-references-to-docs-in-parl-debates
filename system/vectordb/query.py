from system.config import VECTOR_DB_INDEX
from vectordb.embedder import embedding
from vectordb.crud import es

def query_vector_database(query_text, top_k=10, year=None, doc_type=None):
    """Query Elasticsearch for similar documents using vector similarity search."""
    # Generate embedding for query
    query_embedding = embedding.dense_encode(query_text)

    # Construct the base script query for vector similarity
    script_score_query = {
        "script_score": {
            "query": {
                "match_all": {}
            },
            "script": {
                "source": "cosineSimilarity(params.query_vector, 'content_embedding') + 1.0",
                "params": {"query_vector": query_embedding}
            }
        }
    }

    # Build the main query using a bool query
    main_query = {
        "bool": {
            "must": [
                script_score_query  # Always include the vector similarity
            ]
        }
    }

    # Add the year filter if a year is provided
    if year:
        year_filter = {
            "range": {
                "date": {
                    "gte": f"{year}-01-01",
                    "lte": f"{year}-12-31",
                    "format": "yyyy-MM-dd" 
                }
            }
        }
        main_query["bool"]["filter"] = [year_filter]

    # Add the document type filter if a type is provided
    if doc_type:
        type_filter = {
            "term": {
                "type": doc_type  # Assuming 'type' is a keyword field in your index
            }
        }
        if "filter" not in main_query["bool"]:
            main_query["bool"]["filter"] = []
        main_query["bool"]["filter"].append(type_filter)

    # Execute the search
    response = es.search(
        index=VECTOR_DB_INDEX,
        body={
            "size": top_k,
            "query": main_query,  # Use the combined bool query
            "_source": ["id", "title", "date", "content", "type"]
        }
    )

    # Format results
    candidates = []
    for hit in response["hits"]["hits"]:
        doc = hit["_source"]
        candidates.append({
            "id": doc["id"],
            "title": doc["title"],
            "date": doc["date"],
            "type": doc.get("type", "unknown"),
            "url": f"https://zoek.officielebekendmakingen.nl/{doc['id']}.html",
            "similarity_score": hit["_score"]
        })

    return candidates