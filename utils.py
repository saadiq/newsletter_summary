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


def smart_extract_content(content: str) -> str:
    """
    Intelligently extract meaningful content from newsletter text by removing noise.
    
    This function:
    1. Removes footer content (unsubscribe, copyright, etc.)
    2. Cleans excessive formatting artifacts
    3. Removes tracking URLs and social media blocks
    4. Preserves the actual news content
    
    Args:
        content: The cleaned markdown/text content from clean_body()
    
    Returns:
        Extracted content with noise removed
    """
    if not content:
        return content
    
    # Find where footer content likely starts
    footer_indicators = [
        'unsubscribe',
        'update your preferences',
        'update preferences',
        'privacy policy',
        'terms of service',
        'terms and conditions',
        '© 20',  # Copyright years
        'copyright 20',
        'forward to a friend',
        'forward this email',
        'why did i get this',
        'sent to',
        'view in your browser',
        'manage your subscription',
        'opt out',
        'stop receiving'
    ]
    
    # Find the earliest footer indicator
    footer_start = len(content)
    for indicator in footer_indicators:
        pos = content.lower().find(indicator.lower())
        if pos > 0 and pos < footer_start:
            # Check if this is too early (less than 50% through content)
            # to avoid cutting actual content that mentions these terms
            if pos / len(content) > 0.5:
                footer_start = pos
    
    # Cut content at footer
    if footer_start < len(content):
        content = content[:footer_start]
    
    # Clean excessive formatting artifacts
    # Remove invisible Unicode characters commonly used for spacing in emails
    content = re.sub(r'[\u200c\u200d\ufeff\u2060\u180e\u200b\u200e\u200f\u202a-\u202e\u2066-\u2069]', '', content)
    
    # Replace runs of bullet characters with single bullets
    content = re.sub(r'[•●▪▫◦‣⁃]{2,}', '•', content)
    content = re.sub(r'[\*\-]{3,}', '---', content)  # Keep horizontal rules but normalize them
    
    # Clean up excessive whitespace
    content = re.sub(r'\n{4,}', '\n\n\n', content)  # Max 3 newlines
    content = re.sub(r'[ \t]{3,}', '  ', content)  # Max 2 spaces/tabs
    content = re.sub(r'^[ \t]+', '', content, flags=re.MULTILINE)  # Remove leading whitespace
    
    # Remove "View in browser" type links at the start
    view_browser_patterns = [
        r'^.*?view\s+in\s+browser.*?\n+',
        r'^.*?read\s+online.*?\n+',
        r'^.*?having\s+trouble\s+viewing.*?\n+',
        r'^.*?email\s+not\s+displaying.*?\n+'
    ]
    for pattern in view_browser_patterns:
        content = re.sub(pattern, '', content, flags=re.IGNORECASE | re.MULTILINE)
    
    # Remove tracking URLs (but keep legitimate article links)
    # This is tricky - we want to keep real links but remove tracking
    tracking_patterns = [
        r'https?://[^\s]*(?:track|click|analytics|pixel|utm_|campaign=|ref=|source=)[^\s]*',
        r'https?://[^\s]*mailchi\.mp[^\s]*',
        r'https?://[^\s]*list-manage\.com[^\s]*',
        r'https?://[^\s]*sendgrid\.net[^\s]*',
        r'https?://[^\s]*mailgun\.[^\s]*'
    ]
    for pattern in tracking_patterns:
        content = re.sub(pattern, '[link]', content)
    
    # Remove social media follow blocks (but keep article references to social media)
    social_blocks = [
        r'follow\s+(?:us\s+)?(?:on\s+)?(?:twitter|facebook|linkedin|instagram|youtube)[^\n]*\n?',
        r'(?:twitter|facebook|linkedin|instagram|youtube)\s*(?:\||•)\s*(?:twitter|facebook|linkedin|instagram|youtube)[^\n]*\n?'
    ]
    for pattern in social_blocks:
        content = re.sub(pattern, '', content, flags=re.IGNORECASE)
    
    # Remove email client instructions
    email_instructions = [
        r'add\s+.*?to\s+your\s+address\s+book[^\n]*\n?',
        r'to\s+ensure\s+delivery[^\n]*\n?',
        r'mark\s+as\s+not\s+spam[^\n]*\n?'
    ]
    for pattern in email_instructions:
        content = re.sub(pattern, '', content, flags=re.IGNORECASE)
    
    # Final cleanup
    content = content.strip()
    
    return content 