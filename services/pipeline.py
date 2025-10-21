import time
import schedule
from pathlib import Path
from paper_fetcher import download_pdfs
from summarizer import process_pdf
from send_email import send_email
from dotenv import load_dotenv
import os

load_dotenv()

def job():
    """The main job to be scheduled."""
    print("🚀 Starting weekly paper summary job...")
    topic = "LLM"
    receiver_email = os.getenv("RECEIVER_EMAIL")
    
    if not receiver_email:
        print("❌ RECEIVER_EMAIL not set in .env file. Aborting.")
        return

    downloaded_files = download_pdfs(topic, max_papers=1)

    if not downloaded_files:
        print("No new papers to process. Exiting.")
        return

    for pdf_path_str in downloaded_files:
        pdf_path = Path(pdf_path_str)
        print(f"📄 Processing: {pdf_path.name}")
        
        summary = process_pdf(pdf_path)
        
        email_subject = f"Research Paper Summary: {pdf_path.stem}"
        email_body = f"Hello,\n\nAttached is the research paper '{pdf_path.stem}' and its structured summary.\n\nBest regards,\nYour Research Assistant\n\n--- SUMMARY ---\n\n{summary}"
        
        send_email(email_subject, email_body, receiver_email, str(pdf_path))

if __name__ == "__main__":
    # Run the job once immediately
    job()

    # Schedule the job to run every week
    schedule.every().week.do(job)
    print("✅ Job scheduled to run every week.")

    while True:
        schedule.run_pending()
        time.sleep(1)
