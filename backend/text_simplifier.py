"""
text_simplifier.py

Replaces HuggingFace summarizer with Google Gemini API integration.
Keeps legal jargon replacement, chunking, and final cleanup logic.
"""

import os
import re
import time
from typing import List
import logging

import spacy
import google.generativeai as genai

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load spaCy model (sentence segmentation)
try:
    nlp = spacy.load("en_core_web_sm")
except Exception as e:
    # Helpful error message if model is missing
    logger.error("spaCy model 'en_core_web_sm' not found. Run: python -m spacy download en_core_web_sm")
    raise

# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise EnvironmentError("GEMINI_API_KEY environment variable not set. Add it before running the app.")
genai.configure(api_key=GEMINI_API_KEY)

# Choose model (can change to another Gemini model if available)
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-pro")  # default to gemini-pro; change if needed

class LegalTextSimplifier:
    def __init__(self):
        # Basic legal jargon mappings (you can extend this dictionary)
        self.legal_replacements = {
            "whereas": "while",
            "hereby": "by this document",
            "herein": "in this document",
            "hereinafter": "from now on called",
            "aforementioned": "mentioned before",
            "notwithstanding": "despite",
            "pursuant to": "according to",
            "in lieu of": "instead of",
            "forthwith": "immediately",
            "hereunder": "under this agreement",
            "heretofore": "until now",
            "ipso facto": "by the fact itself",
            "vis-à-vis": "in relation to",
            "inter alia": "among other things",
            "prima facie": "at first sight",
            "quid pro quo": "something for something",
            "sine qua non": "essential requirement",
            "force majeure": "unforeseeable circumstances",
            "caveat emptor": "buyer beware"
        }
        # Configurable chunk size (characters). Gemini can handle large contexts but keep safe limits.
        self.max_chunk_chars = int(os.getenv("MAX_CHUNK_CHARS", 3000))
        # Gemini generation options
        self.max_output_tokens = int(os.getenv("GEMINI_MAX_OUTPUT_TOKENS", 512))
        self.temperature = float(os.getenv("GEMINI_TEMPERATURE", 0.2))
        self.retry_attempts = int(os.getenv("GEMINI_RETRY_ATTEMPTS", 3))
        self.retry_backoff = float(os.getenv("GEMINI_RETRY_BACKOFF", 1.5))

    def chunk_text(self, text: str, max_chunk_size: int = None) -> List[str]:
        """Split text into manageable chunks by sentences without breaking sentence boundaries."""
        if max_chunk_size is None:
            max_chunk_size = self.max_chunk_chars

        doc = nlp(text)
        sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]
        chunks = []
        current_chunk = ""

        for sentence in sentences:
            # If adding sentence exceeds the limit, flush current chunk
            if len(current_chunk) + len(sentence) + 1 <= max_chunk_size:
                current_chunk = (current_chunk + " " + sentence).strip() if current_chunk else sentence
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                # If single sentence itself longer than max_chunk_size, split it forcefully
                if len(sentence) > max_chunk_size:
                    # naive split by characters to ensure progress
                    for i in range(0, len(sentence), max_chunk_size):
                        part = sentence[i:i+max_chunk_size].strip()
                        if part:
                            chunks.append(part)
                    current_chunk = ""
                else:
                    current_chunk = sentence

        if current_chunk:
            chunks.append(current_chunk)

        return chunks

    def replace_legal_jargon(self, text: str) -> str:
        """Replace legal jargon using regex (case-insensitive)."""
        simplified_text = text
        for legal_term, plain_term in self.legal_replacements.items():
            pattern = re.compile(r'\b' + re.escape(legal_term) + r'\b', re.IGNORECASE)
            simplified_text = pattern.sub(plain_term, simplified_text)
        return simplified_text

    def _call_gemini(self, prompt: str) -> str:
        """
        Call Gemini to simplify the provided text chunk.
        Includes simple retry/backoff logic.
        """
        attempt = 0
        while attempt < self.retry_attempts:
            try:
                # model selection - using the high-level generate_content API pattern
                model = genai.GenerativeModel(GEMINI_MODEL)
                # Construct final prompt with clear instructions
                system_instruction = (
                    "You are an assistant specialized in simplifying legal language. "
                    "Rewrite the input legal text in clear, everyday English that a 10th-grade student can understand. "
                    "Use short sentences, familiar words, and avoid complex sentence structures. "
                    "Keep the original meaning and legal obligations intact. "
                    "Preserve all numbers, dates, and percentages exactly. "
                    "Highlight obligations, penalties, deadlines, and durations in plain terms. "
                    "Return only the simplified text without any additional commentary."
                )


                # Compose the instruction prompt for the model
                full_prompt = f"{system_instruction}\n\nLEGAL TEXT:\n{prompt}\n\nSIMPLIFIED TEXT:"
                
                # Call the model
                response = model.generate_content(
                    full_prompt,
                    temperature=self.temperature,
                    max_output_tokens=self.max_output_tokens
                )
                # `response` object may contain .text or .content depending on SDK; try robust access
                text_out = None
                if hasattr(response, "text"):
                    text_out = response.text
                elif hasattr(response, "content"):
                    # Some SDK returns "content" as list of messages
                    if isinstance(response.content, list) and len(response.content) > 0:
                        # join string parts
                        text_out = " ".join([c.get("text", "") if isinstance(c, dict) else str(c) for c in response.content])
                    else:
                        text_out = str(response.content)
                else:
                    # Fallback to string conversion
                    text_out = str(response)

                if not text_out:
                    raise ValueError("Empty response from Gemini")

                return text_out.strip()

            except Exception as e:
                attempt += 1
                wait_time = self.retry_backoff ** attempt
                logger.warning(f"Gemini call failed (attempt {attempt}/{self.retry_attempts}): {e} — retrying in {wait_time:.1f}s")
                time.sleep(wait_time)

        # If all retries fail, raise exception to let caller handle fallback
        raise RuntimeError("Gemini API calls failed after multiple attempts.")

    def summarize_chunk(self, chunk: str) -> str:
        """Use Gemini to simplify a chunk; if it fails, fall back to returning the original chunk (after lite cleanup)."""
        # If chunk is very short, return it unchanged (no need to call API)
        if len(chunk.strip()) < 60:
            return chunk.strip()

        try:
            simplified = self._call_gemini(chunk)
            # minimal sanitization
            simplified = simplified.replace("\r\n", "\n").strip()
            # If output is suspiciously short (e.g., model returned '...'), fall back
            if len(simplified) < max(30, len(chunk) // 8):
                logger.info("Gemini returned short output; falling back to original chunk.")
                return chunk.strip()
            return simplified
        except Exception as e:
            logger.error(f"Summarization with Gemini failed: {e}. Returning original chunk.")
            return chunk.strip()

    def final_cleanup(self, text: str) -> str:
        """Final formatting and whitespace cleanup."""
        # Normalize whitespace
        text = re.sub(r'\r\n', '\n', text)
        text = re.sub(r'[ \t]+', ' ', text)
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)  # collapse multiple blank lines to two
        # Ensure a space after punctuation if missing
        text = re.sub(r'([.!?])([A-Z0-9])', r'\1 \2', text)
        # Trim extra leading/trailing whitespace
        return text.strip()

    def simplify_legal_text(self, text: str) -> str:
        """Main entrypoint to simplify full legal text document."""
        if not text or len(text.strip()) < 50:
            return text

        # 1) Replace jargon with simpler phrases (keeps meaning)
        try:
            replaced = self.replace_legal_jargon(text)
        except Exception as e:
            logger.warning(f"Jargon replacement failed: {e}")
            replaced = text

        # 2) Chunk the text
        chunks = self.chunk_text(replaced)

        # 3) Summarize/simplify each chunk
        simplified_chunks = []
        for idx, chunk in enumerate(chunks):
            logger.info(f"Simplifying chunk like u explain 8th standard student {idx+1}/{len(chunks)} (len={len(chunk)} chars)")
            simplified_chunk = self.summarize_chunk(chunk)
            simplified_chunks.append(simplified_chunk)

        # 4) Combine
        combined = "\n\n".join(simplified_chunks)

        # 5) Final cleanup
        final_text = self.final_cleanup(combined)

        return final_text


# Global instance for the rest of your app to import
legal_simplifier = LegalTextSimplifier()

def simplify_legal_text(text: str) -> str:
    """
    Convenience function matching your previous API:
    from text_simplifier import simplify_legal_text
    """
    return legal_simplifier.simplify_legal_text(text)
