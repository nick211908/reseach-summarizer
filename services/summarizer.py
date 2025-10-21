import os
import re
import fitz  # PyMuPDF
from pathlib import Path
from langchain_google_genai import ChatGoogleGenerativeAI
from pdf2image import convert_from_path
import pytesseract
from dotenv import load_dotenv

load_dotenv()

# --------------------- Config ---------------------
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")  # set your key in env

# --------------------- Helpers ---------------------
def sanitize_filename(name: str) -> str:
    """Clean file names for saving locally."""
    name = re.sub(r"[<>:\"/\\|?*\n]", " ", name)
    return name[:100].strip()

def clean_text_for_ai(text: str) -> str:
    """Clean text for AI processing: remove control characters and normalize spacing."""
    text = re.sub(r"[\x00-\x08\x0B-\x0C\x0E-\x1F]", "", text)  # control chars
    text = re.sub(r"\n{3,}", "\n\n", text)  # multiple newlines
    text = re.sub(r"[ \t]{2,}", " ", text)  # multiple spaces/tabs
    return text.strip()

def extract_pdf_text(pdf_path: Path) -> str:
    """
    Extract text from a PDF.
    - First tries PyMuPDF extraction.
    - If empty, falls back to OCR (pdf2image + pytesseract).
    """
    text = ""

    # --- PyMuPDF extraction ---
    try:
        doc = fitz.open(pdf_path)
        for page in doc:
            page_text = page.get_text("text")
            text += page_text + "\n"
        doc.close()
    except Exception as e:
        print(f"⚠️ PyMuPDF error reading {pdf_path}: {e}")

    # --- Fallback to OCR if no text extracted ---
    if not text.strip():
        print(f"⚠️ No text found, falling back to OCR for {pdf_path}...")
        try:
            pages = convert_from_path(pdf_path)
            for page_image in pages:
                ocr_text = pytesseract.image_to_string(page_image)
                text += ocr_text + "\n"
        except Exception as e:
            print(f"⚠️ OCR failed for {pdf_path}: {e}")

    if not text.strip():
        return "⚠️ No readable text could be extracted from this PDF."

    return clean_text_for_ai(text)

# --------------------- AI Summarization ---------------------
def frame_paper_summary(pdf_text: str, paper_title: str) -> str:
    """
    Use LangChain Google Generative AI to process PDF text
    and generate a structured reading guide.
    """
    llm = ChatGoogleGenerativeAI(api_key=GOOGLE_API_KEY, model="gemini-2.0-flash", temperature=0)
    
    prompt=f"""You are a research assistant. I have provided the text of a research paper. 
Please generate a detailed guide for reading this paper using the following structure:

1. Before You Start: Preparation & Prerequisites
2. Structured Reading Approach
3. Summarizing the Paper
4. Critical Thinking While Reading
5. Projects to implement using this Paper
6. Practical Tips

Please provide the output as **plain text only**, without Markdown symbols like **, *, #, or >. 
Use numbered lists and simple indentation for subpoints. Make it easy to read in plain text format.

Paper Title: {paper_title}

Paper Text (first 5000 characters): {pdf_text}"""
    
    response = llm.invoke([{"role": "user", "content": prompt}])
    return response.content if response else "⚠️ AI could not generate the summary."

# --------------------- Pipeline ---------------------
def process_pdf(pdf_path: Path) -> str:
    pdf_text = extract_pdf_text(pdf_path)
    paper_title = sanitize_filename(pdf_path.stem)
    summary = frame_paper_summary(pdf_text, paper_title)
    return summary

# --------------------- Example Usage ---------------------
if __name__ == "__main__":
    pdf_file = r"D:\Project\research-paper-summarizer\services\data\PolySkill Learning Generalizable Skills Through Polymorphic Abstraction.pdf"
    pdf_path = Path(pdf_file)
    if not pdf_path.exists():
        print(f"❌ File does not exist: {pdf_path}")
    else:
        summary = process_pdf(pdf_path)
        print("\n" + "="*80 + "\n")
        print(summary)
