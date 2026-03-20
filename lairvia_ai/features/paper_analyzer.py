import logging
import re
from collections import Counter, defaultdict
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class PaperAnalyzer:
    """Analyze question papers to detect patterns and statistics"""
    
    def __init__(self):
        self.logger = logger
    
    def analyze(self, paper_text: str) -> Dict[str, Any]:
        """
        Analyze the given question paper text
        
        Returns:
            analysis dict containing question types, marks distribution, frequent keywords, and suggested focus areas
        """
        if not paper_text:
            return {}
        
        questions = self._split_questions(paper_text)
        q_types = self._detect_question_types(questions)
        marks = self._extract_marks(questions)
        freq_keywords = self._top_keywords(paper_text, top_n=20)
        topic_freq = self._topic_frequency(questions)
        
        analysis = {
            "total_questions": len(questions),
            "question_types": q_types,
            "marks_distribution": marks,
            "frequent_keywords": freq_keywords,
            "topic_frequency": topic_freq,
            "recommendations": self._recommendations(topic_freq, freq_keywords)
        }
        self.logger.info("Paper analysis completed")
        return analysis
    
    def _split_questions(self, text: str) -> List[str]:
        """Split paper into question strings using heuristics"""
        # Split by line breaks where lines start with numbers or Q.
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        questions = []
        current = []
        for line in lines:
            if re.match(r'^(Q|Question|\d+[\.\)])\s', line, re.IGNORECASE) or re.match(r'^\d+\s+', line):
                if current:
                    questions.append(" ".join(current).strip())
                current = [line]
            else:
                current.append(line)
        if current:
            questions.append(" ".join(current).strip())
        return questions
    
    def _detect_question_types(self, questions: List[str]) -> Dict[str, int]:
        """Detect types like MCQ, short answer, long answer, numerical"""
        types = Counter()
        for q in questions:
            q_lower = q.lower()
            if any(k in q_lower for k in ["choose", "option", "mcq", "multiple choice"]):
                types["mcq"] += 1
            elif any(k in q_lower for k in ["explain", "discuss", "describe", "evaluate"]):
                types["long_answer"] += 1
            elif any(k in q_lower for k in ["define", "what is", "state", "short answer"]):
                types["short_answer"] += 1
            elif re.search(r'\b\d{1,3}\s?marks\b', q_lower) or re.search(r'\bmarks?\b', q_lower):
                types["marked_question"] += 1
            else:
                # fallback by length
                if len(q.split()) < 20:
                    types["short_answer"] += 1
                else:
                    types["long_answer"] += 1
        return dict(types)
    
    def _extract_marks(self, questions: List[str]) -> Dict[str, int]:
        """Extract marks distribution using regex"""
        marks = Counter()
        for q in questions:
            m = re.search(r'(\d{1,3})\s?marks?', q, re.IGNORECASE)
            if m:
                marks[int(m.group(1))] += 1
        return dict(marks)
    
    def _top_keywords(self, text: str, top_n: int = 20) -> List[tuple]:
        """Return top keywords excluding stopwords"""
        import re
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        stopwords = set([
            "the","and","for","with","that","this","from","which","when","what",
            "where","are","were","was","has","have","been","its","their","they",
            "can","will","shall","may","also","such","these"
        ])
        filtered = [w for w in words if w not in stopwords]
        c = Counter(filtered)
        return c.most_common(top_n)
    
    def _topic_frequency(self, questions: List[str]) -> Dict[str, int]:
        """Try to infer topic frequency by common noun phrases"""
        import re
        topics = []
        for q in questions:
            # find capitalized phrases or noun chunks heuristically
            caps = re.findall(r'\b([A-Z][a-z]{2,}(?:\s+[A-Z][a-z]{2,})*)\b', q)
            for cap in caps:
                topics.append(cap)
        c = Counter(topics)
        return dict(c.most_common(20))
    
    def _recommendations(self, topic_freq: Dict[str, int], keywords: List[tuple]) -> List[str]:
        """Generate study recommendations"""
        recs = []
        if topic_freq:
            top_topics = list(topic_freq.keys())[:5]
            recs.append(f"Focus on topics: {', '.join(top_topics)}")
        if keywords:
            top_k = ", ".join([k for k, _ in keywords[:10]])
            recs.append(f"Revise frequently occurring keywords: {top_k}")
        recs.append("Practice long-form answers for descriptive questions.")
        recs.append("Allocate time based on marks distribution; prioritize high-mark questions.")
        return recs
