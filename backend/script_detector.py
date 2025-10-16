import re

# Unicode script ranges
DEVANAGARI_START = '\u0900'
DEVANAGARI_END = '\u097F'
TELUGU_START = '\u0C00'
TELUGU_END = '\u0C7F'

def is_devanagari(text):
    """Check if text contains Devanagari (Hindi) script"""
    return any(DEVANAGARI_START <= char <= DEVANAGARI_END for char in text)

def is_telugu(text):
    """Check if text contains Telugu script"""
    return any(TELUGU_START <= char <= TELUGU_END for char in text)

def is_roman(text):
    """Check if text consists primarily of Latin characters"""
    # Includes common punctuation and Latin extended characters for accented letters
    return re.fullmatch(r'[a-zA-Z0-9\s\.,?!:;\'"()\[\]\-\u00C0-\u00FF]+', text) is not None

def detect_script(text):
    """
    Detects the script/language style of the input text.
    Returns specific script type to help AI respond in matching format.
    """
    if not text or not text.strip():
        return "unknown"
    
    # Check for native scripts first
    if is_telugu(text):
        return "telugu"  # Native Telugu script (తెలుగు)
    
    elif is_devanagari(text):
        return "hindi"  # Native Hindi script (हिंदी)
    
    elif is_roman(text):
        lower = text.lower()
        words = set(re.findall(r'\b\w+\b', lower)) # Tokenize into words

        # =================================================================
        # NEW HIGH-CONFIDENCE ENGLISH CHECK (CRITICAL FIX)
        # =================================================================
        # Check for common English function words
        english_function_words = {"what", "is", "this", "that", "how", "are", "you", "my", "me", "look", "tell", "place", "get", "lost"}
        english_word_count = sum(1 for word in words if word in english_function_words)
        
        # If a short input (e.g., <= 5 words) has a high proportion of English words, prioritize English.
        if len(words) > 0 and english_word_count / len(words) > 0.4:
            return "english"
        # =================================================================
        
        # Enhanced Telugu romanization detection
        telugu_words = [
            "ela", "unnav", "em", "chesthunnav", "cheppandi", "enti", "ledu", "kadu", "avunu", 
            "avuna", "enti", "ledhu", "kuda", "ra", "po", "enduku", "ekkada", "epudu", "evaru",
            "nenu", "nuvvu", "meeru", "vadu", "vaadu", "adi", "idi",
            "chesthunnav", "chesthunnaanu", "chesaanu", "chesav",
            "raavaddu", "raa", "vellanu", "vellaanu", "kaavalenu",
            "bagunnav", "bagundi", "manchidi", "thanks", "dhanyavaadalu"
        ]
        
        # Enhanced Hindi romanization detection
        hindi_words = [
            "kya", "hai", "aap", "mera", "tera", "tumhara", "tum", "hum", "main",
            "chahiye", "kaise", "kahan", "kab", "kyun", "kaun",
            "achha", "theek", "nahi", "haan", "mujhe", "tumhe", "usse",
            "karoge", "karunga", "kiya", "karta", "karti", "ho",
            "raha", "rahe", "rahi", "tha", "the", "thi",
            "dhanyavaad", "shukriya", "namaste", "yeh", "woh"
        ]
        
        # Count matches for both languages
        telugu_matches = sum(1 for word in telugu_words if word in lower)
        hindi_matches = sum(1 for word in hindi_words if word in lower)
        
        # Determine which language based on matches
        if telugu_matches > 0 and telugu_matches >= hindi_matches:
            return "roman-telugu"
        elif hindi_matches > 0:
            return "roman-hindi"
        else:
            # Final fallback for Roman text
            return "english"

    # Default fallback for any other script
    return "unknown"