import datetime
from typing import List, Optional, Dict, Any
import base64
import re
from tqdm import tqdm
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

def retry_with_backoff(max_retries: int = 3, base_delay: float = 1.0):
    """Decorator for retrying functions with exponential backoff."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt)
                        time.sleep(delay)
                    else:
                        raise last_exception
            return None
        return wrapper
    return decorator

@retry_with_backoff(max_retries=3, base_delay=0.5)
def fetch_single_newsletter(service, message_id: str, pbar_lock: threading.Lock = None, pbar = None) -> Optional[Dict[str, Any]]:
    """Fetch a single newsletter with error handling."""
    try:
        msg = service.users().messages().get(userId='me', id=message_id, format='full').execute()
        payload = msg['payload']
        headers = payload['headers']
        subject = next((header['value'] for header in headers if header['name'] == 'Subject'), 'No Subject')
        date = next((header['value'] for header in headers if header['name'] == 'Date'), 'No Date')
        sender = next((header['value'] for header in headers if header['name'] == 'From'), 'Unknown Sender')
        body = ""
        body_format = None
        if 'parts' in payload:
            html_body = None
            text_body = None
            for part in payload['parts']:
                if part['mimeType'] == 'text/html':
                    html_body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                elif part['mimeType'] == 'text/plain':
                    text_body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
            if html_body is not None:
                body = html_body
                body_format = 'html'
            elif text_body is not None:
                body = text_body
                body_format = 'plain'
        elif 'body' in payload and 'data' in payload['body']:
            body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
            body_format = 'plain'
        
        # Update progress bar in thread-safe manner
        if pbar and pbar_lock:
            with pbar_lock:
                pbar.update(1)
        
        return {
            'subject': subject,
            'date': date,
            'sender': sender,
            'body': body,
            'body_format': body_format,
            'id': message_id,
            'status': 'success'
        }
    except Exception as e:
        # Update progress bar even on failure
        if pbar and pbar_lock:
            with pbar_lock:
                pbar.update(1)
        
        return {
            'subject': f'Failed to fetch',
            'date': 'Unknown',
            'sender': 'Unknown',
            'body': '',
            'body_format': None,
            'id': message_id,
            'status': 'failed',
            'error': str(e)
        }

def get_ai_newsletters(
    service,
    days: int = 7,
    label: Optional[str] = 'ai-newsletter',
    from_email: Optional[str] = None,
    to_email: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Get emails matching label, date, and optional from/to filters.
    
    Now with parallel fetching and error resilience.
    """
    date_from = (datetime.datetime.now() - datetime.timedelta(days=days)).strftime('%Y/%m/%d')
    query_parts = [f"after:{date_from}"]
    if label:
        query_parts.insert(0, f"label:{label}")
    if from_email:
        query_parts.append(f"from:{from_email}")
    if to_email:
        query_parts.append(f"to:{to_email}")
    query = ' '.join(query_parts)
    
    # Get message list with retry
    @retry_with_backoff(max_retries=3)
    def get_message_list():
        return service.users().messages().list(userId='me', q=query).execute()
    
    try:
        result = get_message_list()
        messages = result.get('messages', [])
    except Exception as e:
        print(f"Error fetching message list: {str(e)}")
        return []
    
    if not messages:
        return []
    
    # Fetch newsletters in parallel
    newsletters = []
    failed_fetches = []
    
    # Thread-safe progress bar
    pbar_lock = threading.Lock()
    
    # Allow environment variable to control parallel workers (for GitHub Actions)
    import os
    max_workers = int(os.environ.get('NEWSLETTER_PARALLEL_WORKERS', '5'))
    
    # In GitHub Actions, use sequential processing for large batches to avoid memory issues
    if os.environ.get('GITHUB_ACTIONS') and len(messages) > 20:
        max_workers = 1  # Sequential processing for large batches in CI
    
    with tqdm(total=len(messages), desc="Fetching newsletters", unit="email") as pbar:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all fetch tasks
            future_to_message = {
                executor.submit(fetch_single_newsletter, service, msg['id'], pbar_lock, pbar): msg['id'] 
                for msg in messages
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_message):
                message_id = future_to_message[future]
                try:
                    # Shorter timeout in GitHub Actions to prevent hanging
                    timeout = 10 if os.environ.get('GITHUB_ACTIONS') else 30
                    newsletter = future.result(timeout=timeout)
                    if newsletter:
                        if newsletter['status'] == 'success':
                            # Remove status and error fields for successful fetches
                            newsletter.pop('status', None)
                            newsletter.pop('error', None)
                            newsletter.pop('id', None)
                            newsletters.append(newsletter)
                        else:
                            failed_fetches.append({
                                'id': message_id,
                                'error': newsletter.get('error', 'Unknown error')
                            })
                except Exception as e:
                    failed_fetches.append({
                        'id': message_id,
                        'error': f"Timeout or exception: {str(e)}"
                    })
    
    # Report failures if any
    if failed_fetches:
        print(f"\nWarning: Failed to fetch {len(failed_fetches)} newsletter(s):")
        for fail in failed_fetches[:3]:  # Show first 3 failures
            print(f"  - Message {fail['id']}: {fail['error']}")
        if len(failed_fetches) > 3:
            print(f"  ... and {len(failed_fetches) - 3} more")
    
    return newsletters 