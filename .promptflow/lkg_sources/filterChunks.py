from promptflow import tool
from typing import List, Dict, Any, Optional
import re
from ragcore.filterChunks import select_chunks_core
import logging

@tool
def select_chunks(results: List, top_k: int, min_score: float = None, query: str = "") -> List:
    """
    Enhanced chunk selection with dynamic thresholding and query-aware filtering.
    
    Args:
        results: Chunks from the retrieval system
        top_k: Maximum chunks to return
        min_score: Minimum relevance score (can be dynamically adjusted)
        query: Original user query for context-aware filtering
        
    Returns:
        List of selected chunks
    """
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("select_chunks")
    
    # Handle empty results
    if not results or len(results) == 0:
        logger.warning("No results to filter")
        return []
    
    # Dynamic threshold adjustment based on query complexity and results
    adjusted_min_score = adjust_threshold(min_score, query, results)
    logger.info(f"Adjusted min_score from {min_score} to {adjusted_min_score}")
    
    # First pass: get chunks using core function with adjusted threshold
    filtered_chunks = select_chunks_core(results, top_k, adjusted_min_score)
    
    # If we have enough chunks, perform additional filtering and ranking
    if filtered_chunks and len(filtered_chunks) > 0:
        # Post-processing: improve quality and relevance
        filtered_chunks = post_process_chunks(filtered_chunks, query, top_k)
        return filtered_chunks
    else:
        # Fallback: if no chunks pass the threshold, try again with lower threshold
        logger.warning("No chunks passed the threshold, retrying with lower threshold")
        fallback_min_score = adjusted_min_score * 0.7 if adjusted_min_score else 0.3
        return select_chunks_core(results, top_k, fallback_min_score)

def adjust_threshold(min_score: float, query: str, results: List) -> float:
    """
    Dynamically adjust the relevance threshold based on query and results.
    
    Args:
        min_score: Base minimum score
        query: User query
        results: Result chunks
        
    Returns:
        Adjusted minimum score
    """
    # Default threshold if none provided
    if min_score is None:
        min_score = 0.65
    
    # If no query or results, return original
    if not query or not results:
        return min_score
    
    # Check query complexity (simple queries need higher relevance)
    query_terms = query.split()
    query_length = len(query_terms)
    
    # Adjust based on query length
    if query_length <= 3:
        # Short queries should have stricter filtering (more precise)
        return min_score * 1.1  # Increase threshold by 10%
    elif query_length >= 10:
        # Complex queries can be more lenient
        return min_score * 0.9  # Decrease threshold by 10%
    
    # Check results distribution
    if len(results) > 0:
        # If we have many high-quality results, we can be more selective
        try:
            # Flatten all chunks from all results
            all_chunks = []
            for result_set in results:
                if isinstance(result_set, list):
                    all_chunks.extend(result_set)
                    
            # If we have many good results, be more selective
            if len(all_chunks) > top_k * 3:
                return min_score * 1.05  # Slight increase
        except Exception as e:
            # On any error, just use original threshold
            logging.error(f"Error analyzing results: {str(e)}")
    
    return min_score

def post_process_chunks(chunks: List[Dict[str, Any]], query: str, top_k: int) -> List[Dict[str, Any]]:
    """
    Perform post-processing on selected chunks to improve quality.
    
    Args:
        chunks: Selected chunks from core selection
        query: Original user query
        top_k: Maximum chunks to return
        
    Returns:
        Post-processed chunks
    """
    # If no query or chunks, return original
    if not query or not chunks:
        return chunks
    
    # Extract key terms from query for focused matching
    query_terms = extract_key_terms(query)
    
    # Boost scores for chunks with query terms in title or early in content
    for chunk in chunks:
        boost = 0
        
        # Title match is a strong signal
        if 'title' in chunk and chunk['title']:
            title = chunk['title'].lower()
            for term in query_terms:
                if term in title:
                    boost += 0.1  # Boost for each term in title
        
        # Early mention in content is valuable
        if 'content' in chunk and chunk['content']:
            content = chunk['content'].lower()
            first_100_chars = content[:100]
            for term in query_terms:
                if term in first_100_chars:
                    boost += 0.05  # Smaller boost for early mention
        
        # Apply the boost
        if 'score' in chunk and boost > 0:
            chunk['score'] = chunk['score'] * (1 + boost)
    
    # Re-sort by adjusted score
    chunks = sorted(chunks, key=lambda x: x.get('score', 0), reverse=True)
    
    # Ensure diversity by avoiding nearly duplicate content
    deduped_chunks = []
    content_hashes = set()
    
    for chunk in chunks:
        # Create a simple content fingerprint
        if 'content' in chunk and chunk['content']:
            # Simple fingerprinting: first 100 chars + last 100 chars
            content = chunk['content']
            fingerprint = (content[:100] + content[-100:]).lower()
            
            # Skip if too similar to existing chunk
            if fingerprint in content_hashes:
                continue
                
            content_hashes.add(fingerprint)
        
        deduped_chunks.append(chunk)
        
        # Stop once we have enough
        if len(deduped_chunks) >= top_k:
            break
    
    return deduped_chunks[:top_k]

def extract_key_terms(query: str) -> List[str]:
    """Extract key terms from the query for matching."""
    # Remove stop words for more focused matching
    stop_words = {'a', 'an', 'the', 'and', 'or', 'but', 'is', 'are', 'was', 'were', 
                 'be', 'been', 'being', 'in', 'on', 'at', 'to', 'for', 'with', 
                 'about', 'against', 'between', 'into', 'through', 'during', 
                 'before', 'after', 'above', 'below', 'from', 'up', 'down', 
                 'of', 'off', 'over', 'under', 'again', 'further', 'then', 
                 'once', 'here', 'there', 'when', 'where', 'why', 'how', 
                 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 
                 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 
                 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 
                 'don', 'should', 'now'}
    
    # Tokenize and clean
    query = query.lower()
    query = re.sub(r'[^\w\s]', ' ', query)  # Remove punctuation
    terms = query.split()
    
    # Filter out stop words and keep terms longer than 2 chars
    key_terms = [term for term in terms if term not in stop_words and len(term) > 2]
    
    return key_terms