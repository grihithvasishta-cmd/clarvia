import logging
import random
import uuid
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class MockTestGenerator:
    """Generate mock tests from study material"""
    
    def __init__(self, num_questions: int = 20):
        self.logger = logger
        self.num_questions = num_questions
        self.question_types = ["mcq", "short_answer", "matching"]
    
    def generate(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate mock test from structured content
        
        Args:
            structure: Structured content
            
        Returns:
            Mock test with questions and answers
        """
        mock_test = {
            "title": "Mock Test",
            "total_questions": 0,
            "questions": [],
            "answer_key": {}
        }
        
        # Extract content for questions
        content = structure.get("content", "")
        chunks = self._split_into_sentences(content)
        random.shuffle(chunks)
        
        num_mcq = max(1, int(self.num_questions * 0.6))
        num_short = max(1, int(self.num_questions * 0.3))
        num_matching = max(0, self.num_questions - num_mcq - num_short)
        
        mcqs = self._generate_mcqs(chunks, num_mcq)
        short_ans = self._generate_short_answers(chunks, num_short)
        matching = self._generate_matching(chunks, num_matching)
        
        all_qs = mcqs + short_ans + matching
        random.shuffle(all_qs)
        
        mock_test["questions"] = all_qs
        mock_test["total_questions"] = len(all_qs)
        for q in all_qs:
            if "answer" in q:
                mock_test["answer_key"][q["id"]] = q["answer"]
        
        self.logger.info(f"Generated mock test with {len(all_qs)} questions")
        return mock_test
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences with basic heuristics"""
        import re
        if not text:
            return []
        sentences = re.split(r'(?<=[.!?])\s+', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        return sentences
    
    def _generate_mcqs(self, chunks: List[str], n: int) -> List[Dict[str, Any]]:
        """Generate MCQs from chunks"""
        mcqs = []
        candidates = [c for c in chunks if " is " in c.lower() or "are " in c.lower() or "refers to" in c.lower() or "defined as" in c.lower()]
        if not candidates:
            candidates = chunks[:]
        random.shuffle(candidates)
        
        for i in range(min(n, len(candidates))):
            sentence = candidates[i]
            qid = str(uuid.uuid4())
            question_text, answer, options = self._create_mcq_from_sentence(sentence)
            mcqs.append({
                "id": qid,
                "type": "mcq",
                "question": question_text,
                "options": options,
                "answer": answer
            })
        return mcqs
    
    def _create_mcq_from_sentence(self, sentence: str):
        """Create a single MCQ by blanking a key phrase"""
        # Heuristic: find a noun phrase before 'is' or 'are' and blank it
        lower = sentence.lower()
        if " is " in lower:
            parts = sentence.split(" is ", 1)
            blank_target = parts[0].strip().split()[-1]
            question_text = parts[0].replace(blank_target, "_____") + " is " + parts[1]
            correct = blank_target.strip().strip(',.')
        elif " are " in lower:
            parts = sentence.split(" are ", 1)
            blank_target = parts[0].strip().split()[-1]
            question_text = parts[0].replace(blank_target, "_____") + " are " + parts[1]
            correct = blank_target.strip().strip(',.')
        elif "refers to" in lower:
            parts = sentence.split("refers to", 1)
            blank_target = parts[0].strip().split()[-1]
            question_text = parts[0].replace(blank_target, "_____") + "refers to" + parts[1]
            correct = blank_target.strip().strip(',.')
        else:
            words = [w.strip(',.') for w in sentence.split() if len(w.strip(',.')) > 3]
            if not words:
                words = sentence.split()
            correct = words[0]
            question_text = sentence.replace(correct, "_____", 1)
        
        # Build distractors using simple heuristics: alter characters or pick neighboring words
        options = [correct]
        distractors = self._generate_distractors(correct, sentence)
        for d in distractors:
            if d not in options:
                options.append(d)
            if len(options) >= 4:
                break
        random.shuffle(options)
        return question_text, correct, options
    
    def _generate_distractors(self, correct: str, sentence: str) -> List[str]:
        """Generate distractor options"""
        distractors = []
        # Try to pick other nouns from sentence
        import re
        words = re.findall(r'\b[A-Za-z]{4,}\b', sentence)
        candidates = [w for w in words if w.lower() != correct.lower()]
        random.shuffle(candidates)
        for c in candidates[:5]:
            distractors.append(c)
        # If not enough, create variants
        if len(distractors) < 3:
            # simple mutations
            distractors += [correct + "s", correct + "ing", correct[::-1]]
        # Clean and limit
        cleaned = []
        for d in distractors:
            dd = d.strip('.,;:()[]')
            if dd and dd.lower() != correct.lower():
                cleaned.append(dd)
        return cleaned[:3]
    
    def _generate_short_answers(self, chunks: List[str], n: int) -> List[Dict[str, Any]]:
        """Generate short answer questions"""
        short_qs = []
        candidates = [c for c in chunks if len(c.split()) < 50]
        if not candidates:
            candidates = chunks[:]
        random.shuffle(candidates)
        
        for i in range(min(n, len(candidates))):
            sentence = candidates[i]
            qid = str(uuid.uuid4())
            question_text, answer = self._create_short_answer_from_sentence(sentence)
            short_qs.append({
                "id": qid,
                "type": "short_answer",
                "question": question_text,
                "answer": answer
            })
        return short_qs
    
    def _create_short_answer_from_sentence(self, sentence: str):
        """Turn a sentence into a short answer question by asking 'What is ...?'"""
        # Heuristic: if sentence contains " is " -> ask "What is X?"
        lower = sentence.lower()
        if " is " in lower:
            subject = sentence.split(" is ", 1)[0]
            predicate = sentence.split(" is ", 1)[1]
            question = f"What is {subject.strip()}?"
            answer = predicate.strip().strip('.')
            return question, answer
        else:
            # Fallback: ask a comprehension question
            truncated = sentence if len(sentence) < 120 else sentence[:120] + "..."
            question = f"Explain: {truncated}"
            answer = sentence
            return question, answer
    
    def _generate_matching(self, chunks: List[str], n: int) -> List[Dict[str, Any]]:
        """Generate matching questions (pairs)"""
        matching_qs = []
        if n <= 0:
            return matching_qs
        pairs = []
        candidates = [c for c in chunks if len(c.split()) < 100][:n*2]
        for c in candidates:
            # create term and definition
            if " is " in c.lower():
                lhs = c.split(" is ", 1)[0].strip()
                rhs = c.split(" is ", 1)[1].strip().strip('.')
            else:
                words = c.split()
                lhs = words[0].strip(',.')
                rhs = " ".join(words[1:6]).strip(',.') + "..."
            pairs.append((lhs, rhs))
        # Build a single matching question containing up to n pairs
        qid = str(uuid.uuid4())
        pairs = pairs[:n]
        left = [p[0] for p in pairs]
        right = [p[1] for p in pairs]
        shuffled_right = right[:]
        random.shuffle(shuffled_right)
        matching_qs.append({
            "id": qid,
            "type": "matching",
            "question": "Match the following terms with their definitions:",
            "left": left,
            "right": shuffled_right,
            "answer": {i: right.index(p[1]) for i, p in enumerate(pairs)}
        })
        return matching_qs
