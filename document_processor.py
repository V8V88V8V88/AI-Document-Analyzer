import PyPDF2
import io
import streamlit as st

class DocumentProcessor:
    """Handles document text extraction from various file formats"""
    
    def __init__(self):
        self.supported_formats = ['pdf', 'txt']
    
    def extract_text(self, uploaded_file):
        """Extract text from uploaded file based on its type"""
        file_extension = uploaded_file.name.split('.')[-1].lower()
        
        if file_extension == 'pdf':
            return self._extract_from_pdf(uploaded_file)
        elif file_extension == 'txt':
            return self._extract_from_txt(uploaded_file)
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")
    
    def _extract_from_pdf(self, uploaded_file):
        """Extract text from PDF file"""
        try:
            # Create a PDF reader object
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
            
            # Extract text from all pages
            text = ""
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n"
            
            if not text.strip():
                raise ValueError("No text could be extracted from the PDF")
            
            return text.strip()
        
        except Exception as e:
            raise ValueError(f"Error extracting text from PDF: {str(e)}")
    
    def _extract_from_txt(self, uploaded_file):
        """Extract text from TXT file"""
        try:
            # Read the text file
            text = uploaded_file.read().decode('utf-8')
            
            if not text.strip():
                raise ValueError("The text file appears to be empty")
            
            return text.strip()
        
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                uploaded_file.seek(0)
                text = uploaded_file.read().decode('latin-1')
                return text.strip()
            except Exception as e:
                raise ValueError(f"Error reading text file: {str(e)}")
        
        except Exception as e:
            raise ValueError(f"Error extracting text from TXT file: {str(e)}")
    
    def validate_file_size(self, uploaded_file, max_size_mb=10):
        """Validate file size (optional utility method)"""
        file_size = len(uploaded_file.getvalue())
        max_size_bytes = max_size_mb * 1024 * 1024
        
        if file_size > max_size_bytes:
            raise ValueError(f"File size ({file_size / 1024 / 1024:.1f} MB) exceeds maximum allowed size ({max_size_mb} MB)")
        
        return True
    
    def get_document_stats(self, text):
        """Get basic statistics about the document"""
        words = text.split()
        paragraphs = text.split('\n\n')
        
        return {
            'character_count': len(text),
            'word_count': len(words),
            'paragraph_count': len([p for p in paragraphs if p.strip()])
        }
