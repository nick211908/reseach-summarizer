import os
import re
import requests
import feedparser
from pathlib import Path
import fitz  # PyMuPDF

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

def sanitize_filename(name: str) -> str:
    """Clean a string so it can safely be used as a filename."""
    name = name.replace("\n", " ").replace("\r", " ").replace("\t", " ")
    name = re.sub(r"[<>:\"/\\|?*]", "", name)
    name = re.sub(r"\s{2,}", " ", name).strip()
    return name[:100]  # limit filename length

def fetch_recent_arxiv_papers(topic: str, max_papers: int = 3):
    """Fetch recent papers from arXiv API."""
    print(f"🔍 Searching for recent papers on: '{topic}'...")
    base_url = "https://export.arxiv.org/api/query"
    params = {
        "search_query": topic.replace(" ", "+"),
        "start": 0,
        "max_results": max_papers,
        "sortBy": "submittedDate",
        "sortOrder": "descending"
    }
    response = requests.get(base_url, params=params)
    feed = feedparser.parse(response.text)
    papers = []
    for entry in feed.entries:
        pdf_url = ""
        for link in entry.links:
            if hasattr(link, "title") and link.title == "pdf":
                pdf_url = link.href
        if pdf_url:
            papers.append({
                "title": entry.title,
                "pdf_url": pdf_url
            })
    return papers

def compress_pdf(input_path: Path, output_path: Path):
    """Compress PDF using PyMuPDF by rewriting it."""
    try:
        doc = fitz.open(input_path)
        doc.save(output_path, deflate=True, garbage=4)
        doc.close()
        return True
    except Exception as e:
        print(f"⚠️ Error compressing PDF {input_path}: {e}")
        return False

def download_pdfs(topic: str, max_papers: int = 3):
    papers = fetch_recent_arxiv_papers(topic, max_papers)
    if not papers:
        print("⚠️ No PDFs found.")
        return []

    downloaded_files = []
    for paper in papers:
        title_clean = sanitize_filename(paper["title"])
        pdf_temp_path = DATA_DIR / f"{title_clean}_temp.pdf"
        pdf_final_path = DATA_DIR / f"{title_clean}.pdf"

        print(f"⬇️ Downloading: {paper['title']}")
        try:
            r = requests.get(paper["pdf_url"], timeout=30)
            r.raise_for_status()
            with open(pdf_temp_path, "wb") as f:
                f.write(r.content)

            # Compress PDF and remove temp file
            if compress_pdf(pdf_temp_path, pdf_final_path):
                downloaded_files.append(str(pdf_final_path))
                print(f"✅ Saved compressed PDF: {pdf_final_path}")
                pdf_temp_path.unlink()  # Always remove temp after compression
            else:
                print(f"⚠️ Compression failed, deleting temp file: {pdf_temp_path}")
                if pdf_temp_path.exists():
                    pdf_temp_path.unlink()  # Remove temp if compression failed
        except Exception as e:
            print(f"⚠️ Error downloading {paper['pdf_url']}: {e}")
            if pdf_temp_path.exists():
                pdf_temp_path.unlink()  # Remove incomplete temp file

    return downloaded_files

if __name__ == "__main__":
    topic = input("Enter a topic: ")
    download_pdfs(topic, max_papers=2)

