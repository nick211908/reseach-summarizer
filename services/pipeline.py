from pathlib import Path
from paper_fetcher import download_pdfs
from summarizer import process_pdf
from send_email import send_email
from dotenv import load_dotenv
import os

load_dotenv()

def main():
    """Main job - fetches papers, summarizes them, and sends via email."""
    print("🚀 Starting paper summary job...")
    
    # Get configuration from environment
    topic = os.getenv("TOPIC", "LLM")  # Default to LLM if not set
    receiver_email = os.getenv("RECEIVER_EMAIL")
    max_papers = int(os.getenv("MAX_PAPERS", "1"))
    
    if not receiver_email:
        print("❌ RECEIVER_EMAIL not set. Aborting.")
        return 1

    # Download papers
    print(f"📚 Fetching {max_papers} paper(s) on topic: {topic}")
    downloaded_files = download_pdfs(topic, max_papers=max_papers)

    if not downloaded_files:
        print("⚠️ No new papers to process.")
        return 0

    # Process each paper
    for pdf_path_str in downloaded_files:
        pdf_path = Path(pdf_path_str)
        print(f"\n📄 Processing: {pdf_path.name}")
        
        # Generate summary
        summary = process_pdf(pdf_path)
        
        # Prepare email
        email_subject = f"Research Paper Summary: {pdf_path.stem}"
        email_body = (
            f"Hello,\n\n"
            f"Here is your weekly research paper summary for '{pdf_path.stem}'.\n\n"
            f"Best regards,\n"
            f"Your Research Assistant\n\n"
            f"{'='*80}\n"
            f"SUMMARY\n"
            f"{'='*80}\n\n"
            f"{summary}"
        )
        
        # Send email
        send_email(email_subject, email_body, receiver_email, str(pdf_path))
    
    print(f"\n✅ Job completed successfully! Processed {len(downloaded_files)} paper(s).")
    return 0

if __name__ == "__main__":
    exit(main())