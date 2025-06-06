"""
data vectorizing parameters
"""
vectorizing_params = {
    'chunk_size': 1000,
    'chunk_overlap': 0
}

"""
Retriever parameters
search_type can be similarity, mmr or similarity_threshold
if search_type == similarity, search_kwargs must be like {
    'k': 10 (how many documents tu return)
}
if search_type == mmr, search_kwargs must be like {
    "k": 10, (how many documents to actually return)
    "fetch_k": 20, (how many documents should the search considerate)
    "lambda_mult": 0.5 (ponderation between diversity and similarity, 0 = max diversity, 1 = max similarity)
}
if search_type == similarity_threshold, search_kwargs must be like {
    "score_threshold": 0.8, (minimum threshold of similarity (between 0 and 1)
    "k": 10 (maximum documents number to actually return - optional)
}
optional paramater : "filter" to filter chunks using metadata:
{
    'k': 10 (how many documents tu return),
    "filter": {
        "source": "my-file.txt"
    }
}
"""
retriever_params = {
    'search_type': 'similarity',
    'search_kwargs': {
        "k": 10
    }
}