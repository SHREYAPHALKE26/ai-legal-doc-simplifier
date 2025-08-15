import re
import spacy
from typing import List, Dict
import datetime

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

class ClauseDetector:
    def __init__(self):
        # Keywords that indicate important clauses
        self.important_keywords = {
            'termination': [
                'terminate', 'termination', 'end this agreement', 'cancel',
                'cancellation', 'dissolution', 'expire', 'expiry'
            ],
            'payment': [
                'payment', 'pay', 'fee', 'cost', 'charge', 'invoice',
                'billing', 'due', 'owe', 'refund', 'penalty', 'fine'
            ],
            'liability': [
                'liable', 'liability', 'responsible', 'responsibility',
                'damages', 'compensation', 'indemnify', 'indemnification'
            ],
            'confidentiality': [
                'confidential', 'confidentiality', 'non-disclosure',
                'proprietary', 'trade secret', 'private information'
            ],
            'intellectual_property': [
                'copyright', 'patent', 'trademark', 'intellectual property',
                'proprietary rights', 'ownership'
            ],
            'dispute_resolution': [
                'dispute', 'arbitration', 'mediation', 'litigation',
                'court', 'jurisdiction', 'governing law'
            ],
            'data_privacy': [
                'personal data', 'privacy', 'data protection', 'GDPR',
                'data processing', 'consent', 'data subject'
            ],
            'force_majeure': [
                'force majeure', 'act of god', 'natural disaster',
                'unforeseeable circumstances', 'beyond control'
            ]
        }
        
        # Patterns for detecting dates and deadlines
        self.date_patterns = [
            r'\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b',  # MM/DD/YYYY or MM-DD-YYYY
            r'\b\d{1,2}\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{2,4}\b',
            r'\bwithin\s+\d+\s+(days?|weeks?|months?|years?)\b',
            r'\b\d+\s+(days?|weeks?|months?|years?)\s+(from|after|before)\b'
        ]
        
        # Risk level indicators
        self.high_risk_terms = [
            'penalty', 'fine', 'breach', 'default', 'violation',
            'damages', 'liquidated damages', 'forfeit', 'void',
            'terminate immediately', 'irreparable harm'
        ]

    def extract_sentences_with_keywords(self, text: str, keywords: List[str]) -> List[str]:
        """Extract sentences containing specific keywords"""
        doc = nlp(text)
        matching_sentences = []
        
        for sent in doc.sents:
            sent_text = sent.text.lower()
            if any(keyword.lower() in sent_text for keyword in keywords):
                matching_sentences.append(sent.text.strip())
        
        return matching_sentences

    def detect_dates_and_deadlines(self, text: str) -> List[Dict]:
        """Detect dates and deadlines in the text"""
        deadlines = []
        
        for pattern in self.date_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                context_start = max(0, match.start() - 100)
                context_end = min(len(text), match.end() + 100)
                context = text[context_start:context_end].strip()
                
                deadlines.append({
                    'date_text': match.group(),
                    'context': context,
                    'position': match.start()
                })
        
        return deadlines

    def assess_risk_level(self, text: str) -> str:
        """Assess the risk level of a clause"""
        text_lower = text.lower()
        
        high_risk_count = sum(1 for term in self.high_risk_terms if term in text_lower)
        
        if high_risk_count >= 2:
            return "HIGH"
        elif high_risk_count == 1:
            return "MEDIUM"
        else:
            return "LOW"

    def detect_important_clauses(self, text: str) -> Dict:
        """Main method to detect important clauses"""
        important_clauses = {}
        
        for clause_type, keywords in self.important_keywords.items():
            sentences = self.extract_sentences_with_keywords(text, keywords)
            
            if sentences:
                clause_data = []
                for sentence in sentences:
                    risk_level = self.assess_risk_level(sentence)
                    clause_data.append({
                        'text': sentence,
                        'risk_level': risk_level,
                        'keywords_found': [kw for kw in keywords if kw.lower() in sentence.lower()]
                    })
                
                important_clauses[clause_type] = clause_data
        
        # Add deadlines as a special category
        deadlines = self.detect_dates_and_deadlines(text)
        if deadlines:
            important_clauses['deadlines'] = deadlines
        
        return important_clauses

    def generate_summary_insights(self, clauses: Dict) -> List[str]:
        """Generate human-readable insights about the important clauses"""
        insights = []
        
        if 'termination' in clauses:
            insights.append("⚠️ This document contains termination clauses - review conditions for ending the agreement")
        
        if 'payment' in clauses:
            high_risk_payments = [c for c in clauses['payment'] if c['risk_level'] == 'HIGH']
            if high_risk_payments:
                insights.append("💰 High-risk payment terms detected - check for penalties or fees")
        
        if 'liability' in clauses:
            insights.append("⚖️ Liability clauses present - understand your responsibilities and potential damages")
        
        if 'deadlines' in clauses:
            insights.append(f"📅 {len(clauses['deadlines'])} deadline(s) found - mark important dates on your calendar")
        
        if 'data_privacy' in clauses:
            insights.append("🔒 Data privacy terms included - review how your personal information will be handled")
        
        return insights

# Global instance
clause_detector = ClauseDetector()

def detect_important_clauses(text: str) -> Dict:
    """Main function to detect important clauses"""
    clauses = clause_detector.detect_important_clauses(text)
    insights = clause_detector.generate_summary_insights(clauses)
    
    return {
        'clauses': clauses,
        'insights': insights,
        'total_important_clauses': sum(len(v) for v in clauses.values() if isinstance(v, list))
    }