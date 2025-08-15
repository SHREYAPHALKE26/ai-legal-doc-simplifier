from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
import tempfile
from dotenv import load_dotenv
import os
import google.generativeai as genai

# Load environment variables from .env
load_dotenv()

# Get Gemini API key from environment
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)



# Import our custom modules
from text_extractor import extract_text_from_file
from text_simplifier import simplify_legal_text
from clause_detector import detect_important_clauses

app = Flask(__name__)
CORS(app)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'pdf', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return jsonify({
        "message": "AI Legal Document Simplifier API",
        "version": "1.0.0",
        "endpoints": {
            "/upload": "POST - Upload and process legal document",
            "/health": "GET - Health check"
        }
    })

@app.route("/test-gemini", methods=["GET"])
def test_gemini():
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")  # You can also try "gemini-pro"
        response = model.generate_content("Simplify: This Agreement shall be governed by the laws of India.")
        return {"simplified_text": response.text}
    except Exception as e:
        return {"error": str(e)}, 500


@app.route('/health')
def health_check():
    return jsonify({"status": "healthy"})

@app.route('/upload', methods=['POST'])
def upload_and_process():
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        if not allowed_file(file.filename):
            return jsonify({"error": "File type not allowed. Please upload PDF or DOCX files."}), 400
        
        # Save file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            file.save(temp_file.name)
            temp_filename = temp_file.name
        
        try:
            # Extract text from file
            original_text = extract_text_from_file(temp_filename)
            
            if not original_text.strip():
                return jsonify({"error": "Could not extract text from the document"}), 400
            
            # Simplify the text
            simplified_text = simplify_legal_text(original_text)
            
            # Detect important clauses
            important_clauses = detect_important_clauses(original_text)
            
            # Clean up temporary file
            os.unlink(temp_filename)
            
            return jsonify({
                "success": True,
                "original_text": original_text,
                "simplified_text": simplified_text,
                "important_clauses": important_clauses,
                "filename": secure_filename(file.filename)
            })
            
        except Exception as e:
            # Clean up temporary file in case of error
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)
            raise e
            
    except Exception as e:
        return jsonify({"error": f"Processing failed: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)