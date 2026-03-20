import logging
import re
import uuid
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class FlashcardGenerator:
    """Generate flashcards (Q/A) from content"""
    
    def __init__(self):
        self.logger = logger
    
    def generate(self, structure: Dict[str, Any], max_cards: int = 50) -> List[Dict[str, str]]:
        """
        Generate flashcards from structured content
        
        Args:
            structure: Structured content
            max_cards: maximum number of flashcards to generate
            
        Returns:
            List of flashcards with front/back
        """
        content = structure.get("content", "")
        candidates = self._extract_candidate_sentences(content)
        cards = []
        for sent in candidates[:max_cards]:
            q, a = self._sentence_to_flashcard(sent)
            cards.append({
                "id": str(uuid.uuid4()),
                "front": q,
                "back": a
            })
        self.logger.info(f"Generated {len(cards)} flashcards")
        return cards
    
    def _extract_candidate_sentences(self, text: str) -> List[str]:
        """Find sentences likely to produce Q/A pairs"""
        sentences = re.split(r'(?<=[.!?])\s+', text)
        filtered = []
        for s in sentences:
            s = s.strip()
            if len(s) < 20:
                continue
            # Prefer definitional sentences or those with 'is', 'are', 'refers to'
            if re.search(r'\b(is|are|refers to|defined as|means|consists of)\b', s, re.IGNORECASE):
                filtered.append(s)
            # Also include sentences with formulas
            elif re.search(r'=', s) or re.search(r'\bformula\b', s, re.IGNORECASE):
                filtered.append(s)
            # Also include sentences with lists or semicolons
            elif ';' in s or ',' in s and len(s.split(',')) <= 4:
                filtered.append(s)
        # fallback: take first N sentences
        if not filtered:
            filtered = [s for s in sentences if len(s.strip()) > 30][:50]
        return filtered
    
    def _sentence_to_flashcard(self, sentence: str) -> (str, str):
        """Convert a sentence into a flashcard Q/A"""
        s = sentence.strip().rstrip('.')
        # If definitional
        m = re.search(r'^(.*?)(?: is | are | refers to | defined as | means )(.*)', s, re.IGNORECASE)
        if m:
            subject = m.group(1).strip()
            definition = m.group(2).strip()
            question = f"What is {subject}?"
            answer = definition
            return question, answer
        # If contains formula
        if '=' in s:
            parts = s.split('=')
            left = parts[0].strip()
            right = "=".join(parts[1:]).strip()
            question = f"What does {left} represent?"
            answer = right
            return question, answer
        # Fallback Q/A: short prompt
        question = f"Explain: {s[:80]}..."
        answer = s
        return question, answer
