# document_processor.py
import PyPDF2
from docx import Document
import email
from email.mime.text import MIMEText
from typing import List, Dict, Any
import hashlib
import logging
from ..models import DocumentChunk
from langchain.text_splitter import RecursiveCharacterTextSplitter

class DocumentProcessor:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        self.logger = logging.getLogger(__name__)
    
    async def process_pdf(self, file_path: str) -> Dict[str, Any]:
        """Extract text from PDF files"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                page_count = len(pdf_reader.pages)
                
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                
                return {
                    "text": text,
                    "page_count": page_count,
                    "metadata": {
                        "total_pages": page_count,
                        "extraction_method": "PyPDF2"
                    }
                }
        except Exception as e:
            self.logger.error(f"Error processing PDF: {str(e)}")
            raise
    
    async def process_docx(self, file_path: str) -> Dict[str, Any]:
        """Extract text from DOCX files"""
        try:
            doc = Document(file_path)
            text = ""
            paragraph_count = 0
            
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text += paragraph.text + "\n"
                    paragraph_count += 1
            
            return {
                "text": text,
                "page_count": None,
                "metadata": {
                    "paragraph_count": paragraph_count,
                    "extraction_method": "python-docx"
                }
            }
        except Exception as e:
            self.logger.error(f"Error processing DOCX: {str(e)}")
            raise
    
    async def process_email(self, file_path: str) -> Dict[str, Any]:
        """Extract text from email files"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                email_content = email.message_from_file(file)
            
            text = ""
            subject = email_content.get('Subject', '')
            sender = email_content.get('From', '')
            date = email_content.get('Date', '')
            
            # Extract body
            if email_content.is_multipart():
                for part in email_content.walk():
                    if part.get_content_type() == "text/plain":
                        text += part.get_payload(decode=True).decode('utf-8', errors='ignore')
            else:
                text = email_content.get_payload(decode=True).decode('utf-8', errors='ignore')
            
            full_text = f"Subject: {subject}\nFrom: {sender}\nDate: {date}\n\n{text}"
            
            return {
                "text": full_text,
                "page_count": None,
                "metadata": {
                    "subject": subject,
                    "sender": sender,
                    "date": date,
                    "extraction_method": "email-parser"
                }
            }
        except Exception as e:
            self.logger.error(f"Error processing email: {str(e)}")
            raise
    
    async def create_chunks(self, text: str, document_id: str, metadata: Dict[str, Any]) -> List[DocumentChunk]:
        """Split text into chunks for embedding"""
        try:
            chunks = self.text_splitter.split_text(text)
            document_chunks = []
            
            for i, chunk_text in enumerate(chunks):
                chunk_id = hashlib.md5(f"{document_id}_{i}_{chunk_text[:50]}".encode()).hexdigest()
                
                chunk = DocumentChunk(
                    chunk_id=chunk_id,
                    document_id=document_id,
                    content=chunk_text,
                    chunk_index=i,
                    metadata={
                        **metadata,
                        "chunk_length": len(chunk_text),
                        "chunk_position": i
                    }
                )
                document_chunks.append(chunk)
            
            return document_chunks
        except Exception as e:
            self.logger.error(f"Error creating chunks: {str(e)}")
            raise
