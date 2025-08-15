# AI Legal Document Simplifier

**A web app that simplifies legal documents into plain English using Google Gemini.**

## Features
- Upload PDF / DOCX
- Text extraction (PyMuPDF, python-docx)
- Simplification using Google Gemini
- Important clause detection (termination, payment, liability, privacy)
- Side-by-side original & simplified text

## Tech stack
- Backend: Flask
- NLP: spaCy
- Gemini integration: google-generativeai
- File parsing: PyMuPDF, python-docx

## Quickstart (local)
1. Clone repo:
   git clone https://github.com/<your-username>/<repo-name>.git
   cd <repo-name>

2. Create virtual env & install:
    python -m venv venv
    source venv/bin/activate   # Windows: venv\Scripts\activate
    pip install -r requirements.txt
    python -m spacy download en_core_web_sm


3. Set secrets:
    echo "GEMINI_API_KEY=your_key_here" > .env


4. Run: python app.py


5. Open: http://127.0.0.1:5000/

## API endpoints
- GET / health/info
- GET /health health check
- POST /upload upload a PDF/DOCX file in multipart/form-data with key file

## Notes
- Do not commit .env. Use GitHub Actions secrets or your host's config to set production environment variables.
- Limit file sizes (server config sets 16MB by default).

## License

MIT

---

Initialize git locally and make the first commit
Open a terminal in your project folder and run:

git init
git add .
git commit -m "Initial commit — AI Legal Document Simplifier"