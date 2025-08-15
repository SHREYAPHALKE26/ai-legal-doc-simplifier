
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

<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/9e92c013-362e-41a9-b0e1-aee3a18b8bb1" />
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/0d723e94-dd01-4a43-b214-d399d028045a" />
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/a363e6be-c6ce-4007-ae9a-bccfe9e3a475" />
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/73b9845e-0a37-49da-8223-e83726a783e5" />
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/672aae9f-a77a-4080-bf9d-a87f54545bc5" />
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/fdb6219d-bbf6-48ad-8ef1-8d2db19d8de0" />




