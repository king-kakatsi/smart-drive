"""
Text processing utilities for document analysis
"""
import re
from typing import List, Dict, Any


def clean_text(text: str) -> str:
    """Clean and normalize text content"""
    if not text:
        return ""

    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text.strip())

    # Remove control characters
    text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)

    return text


def split_into_sentences(text: str) -> List[str]:
    """Split text into sentences"""
    # Simple sentence splitting (can be improved with NLP libraries)
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())

    # Filter out empty sentences
    return [s.strip() for s in sentences if s.strip()]


def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
    """Extract keywords from text (simple frequency-based approach)"""
    if not text:
        return []

    # Clean text
    clean = clean_text(text).lower()

    # Remove punctuation
    clean = re.sub(r'[^\w\s]', ' ', clean)

    # Split into words
    words = clean.split()

    # Remove common stop words (basic list)
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
        'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these',
        'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him',
        'her', 'us', 'them', 'my', 'your', 'his', 'its', 'our', 'their'
    }

    # Filter words
    filtered_words = [word for word in words if len(word) > 2 and word not in stop_words]

    # Count frequency
    word_freq = {}
    for word in filtered_words:
        word_freq[word] = word_freq.get(word, 0) + 1

    # Sort by frequency and return top keywords
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    return [word for word, freq in sorted_words[:max_keywords]]


def calculate_text_similarity(text1: str, text2: str) -> float:
    """Calculate simple text similarity (Jaccard similarity)"""
    if not text1 or not text2:
        return 0.0

    # Clean and tokenize
    words1 = set(clean_text(text1).lower().split())
    words2 = set(clean_text(text2).lower().split())

    # Calculate Jaccard similarity
    intersection = words1.intersection(words2)
    union = words1.union(words2)

    if not union:
        return 0.0

    return len(intersection) / len(union)


def truncate_text(text: str, max_length: int = 1000, suffix: str = "...") -> str:
    """Truncate text to maximum length"""
    if len(text) <= max_length:
        return text

    return text[:max_length - len(suffix)] + suffix


def format_timestamp(seconds: float) -> str:
    """Format seconds into readable timestamp"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes}:{secs:02d}"


def highlight_search_terms(text: str, search_terms: List[str]) -> str:
    """Highlight search terms in text (for display purposes)"""
    if not search_terms:
        return text

    result = text
    for term in search_terms:
        # Case-insensitive replacement
        pattern = re.compile(re.escape(term), re.IGNORECASE)
        result = pattern.sub(f"**{term}**", result)

    return result


