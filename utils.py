from __future__ import annotations
import re
from typing import Optional
from bs4 import BeautifulSoup
from html_to_markdown import convert_to_markdown

def clean_body(html: Optional[str], body_format: Optional[str] = None) -> str:
    if not html:
        return "[Empty email content]"
    
    # If it's already plain text, just return it
    if body_format == 'plain':
        return html
    
    try:
        soup = BeautifulSoup(html, "html.parser")
        
        # Remove problematic tags
        for tag in soup(['style', 'script', 'meta', 'link']):
            tag.decompose()
        
        # Remove all attributes to simplify HTML
        for tag in soup.find_all(True):
            tag.attrs = {}
        
        cleaned_html = str(soup)
        
        # Try to remove CSS with more specific patterns
        cleaned_html = re.sub(r'(?s)@media[^{]+{[^}]+}', '', cleaned_html)
        cleaned_html = re.sub(r'(?s)\.[\w\-]+[^{]*{[^}]+}', '', cleaned_html)
        cleaned_html = re.sub(r'(?s){[^}]+}', '', cleaned_html)
        
        # Convert to markdown
        try:
            markdown = convert_to_markdown(cleaned_html, heading_style="atx")
            return markdown
        except Exception as md_error:
            # If markdown conversion fails, try to extract text directly
            text = soup.get_text(separator='\n', strip=True)
            if text:
                return f"[Plain text extraction]\n{text}"
            else:
                return "[Could not extract text content from HTML]"
                
    except Exception as e:
        # Last resort: try to extract any text from the raw HTML
        try:
            # Simple regex to remove HTML tags
            text = re.sub(r'<[^>]+>', '', html)
            text = re.sub(r'\s+', ' ', text).strip()
            if text:
                return f"[Fallback text extraction]\n{text[:3000]}..."
            else:
                return "[ERROR: Could not parse email content]"
        except:
            return "[ERROR: Critical failure in email parsing]" 