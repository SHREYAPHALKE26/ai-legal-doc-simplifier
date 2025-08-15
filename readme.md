<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/692541ef-eb83-4034-ad2e-3b6781f25046" /># AI Legal Document Simplifier

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
   git clone [https://github.com/SHREYAPHALKE26/ai-legal-doc-simplifier.git]
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


<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/6f34a366-c28a-42ac-a4ad-1ba43a63e6eb" />
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/10c4b7d3-0dca-418b-9db7-956a7f23bc00" />
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/f224aa38-5028-4153-abec-463c92a22568" />
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/d7fec2b1-4245-4300-8c75-6351d25db041" />
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/c7ca492c-b0b0-49f3-aa8e-88db2eab4029" />




