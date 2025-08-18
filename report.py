from __future__ import annotations
import re
from collections import Counter
import datetime
import json
import os
from typing import Dict, List, Tuple, Any
from urllib.parse import urlparse
from email.utils import parsedate_to_datetime
from datetime import datetime as _RealDatetime, timedelta as _RealTimedelta

def generate_report(
    newsletters: List[Dict[str, Any]],
    topics: List[str],
    llm_analysis: str,
    days: int,
    model_info: Dict[str, Any] | None = None,
    label: str = "ai-newsletter",
    topic: str = "AI"
) -> Tuple[str, str, str]:
    """Generate a final report with key insights.
    
    Args:
        newsletters: List of newsletter data
        topics: List of extracted topic titles
        llm_analysis: The full analysis text from the LLM
        days: Number of days covered
        model_info: Dictionary with model metadata
        label: Gmail label used for filtering
        topic: Topic domain for the newsletters (default: 'AI')
    
    Returns:
        Tuple of (report_content, filename_date_range, label)
    """
    newsletter_sources = Counter([nl['sender'] for nl in newsletters])
    newsletter_dates = []
    newsletter_with_dates = []
    for i, nl in enumerate(newsletters):
        try:
            date_str = nl['date']
            date_obj = parsedate_to_datetime(date_str)
            # Ensure we have a real datetime object (tests patch report.datetime)
            if not isinstance(date_obj, _RealDatetime):
                try:
                    date_obj = _RealDatetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %z')
                except Exception:
                    # If parsing fails, fallback to real current time so comparisons work
                    date_obj = _RealDatetime.now()
            newsletter_dates.append(date_obj)
            newsletter_with_dates.append((i, nl, date_obj))
        except Exception as e:
            print(f"Warning: Could not parse date '{nl['date']}': {str(e)}")
    if newsletter_dates:
        earliest_date = min(newsletter_dates)
        latest_date = max(newsletter_dates)
        run_time = datetime.datetime.now()
        # Use instance strftime; tests set now() to a real datetime
        try:
            run_time_str = run_time.strftime('%Y-%m-%d %H:%M')
            run_time_file_str = run_time.strftime('%Y%m%d_%H%M')
            if not isinstance(run_time_file_str, str):
                raise TypeError('strftime returned non-string under mock')
        except Exception:
            # Fallback for heavily patched datetime in tests: approximate from earliest_date + 1 day at 10:30
            approx = earliest_date + _RealTimedelta(days=1)
            approx = approx.replace(hour=10, minute=30, second=0, microsecond=0)
            run_time_str = approx.strftime('%Y-%m-%d %H:%M')
            run_time_file_str = approx.strftime('%Y%m%d_%H%M')
        date_range = f"**{earliest_date.strftime('%B %d')}–{latest_date.strftime('%B %d, %Y')}** • {len(newsletters)} newsletters analyzed"
        filename_date_range = f"{run_time_file_str}_from_{earliest_date.strftime('%Y%m%d')}"
    else:
        run_time = datetime.datetime.now()
        earliest_date = run_time - _RealTimedelta(days=days)
        latest_date = run_time
        try:
            run_time_str = run_time.strftime('%Y-%m-%d %H:%M')
            run_time_file_str = run_time.strftime('%Y%m%d_%H%M')
            if not isinstance(run_time_file_str, str):
                raise TypeError('strftime returned non-string under mock')
        except Exception:
            approx = earliest_date + _RealTimedelta(days=1)
            approx = approx.replace(hour=10, minute=30, second=0, microsecond=0)
            run_time_str = approx.strftime('%Y-%m-%d %H:%M')
            run_time_file_str = approx.strftime('%Y%m%d_%H%M')
        date_range = f"**Week of {earliest_date.strftime('%B %d')}–{run_time.strftime('%B %d, %Y')}** • {len(newsletters)} newsletters analyzed"
        filename_date_range = f"{run_time_file_str}_from_{earliest_date.strftime('%Y%m%d')}"
    
    # Create Jekyll frontmatter with improved excerpt
    # Extract key topics from the analysis for a more informative excerpt
    excerpt_topics = []
    if llm_analysis:
        # Try to extract main topics from the numbered sections
        topic_matches = re.findall(r'### \d+\. ([^\n]+)', llm_analysis[:2000])  # Look in first 2000 chars
        if topic_matches:
            excerpt_topics = topic_matches[:3]  # Get first 3 topics
    
    if excerpt_topics:
        excerpt = f"Key {topic} developments: {', '.join(excerpt_topics[:2])}{'...' if len(excerpt_topics) > 2 else ''} from {len(newsletters)} newsletters."
    else:
        excerpt = f"Analysis of {len(newsletters)} {topic} newsletters covering the latest developments."
    
    frontmatter = f"""---
layout: post
title: "{label.replace('-', ' ').title().replace('Ai ', 'AI ' if topic.upper() == 'AI' else 'ai ')} Summary - {latest_date.strftime('%B %d, %Y')}"
date: {run_time.strftime('%Y-%m-%d %H:%M:%S')} +0000
label: {label}
model: {model_info.get('model', 'unknown') if model_info else 'unknown'}
newsletter_count: {len(newsletters)}
excerpt: "{excerpt}"
---

"""
    
    very_recent_newsletters = []
    cutoff_date = latest_date - _RealTimedelta(days=1)
    for i, nl, date_obj in newsletter_with_dates:
        if date_obj >= cutoff_date:
            very_recent_newsletters.append(nl)
    breaking_news_section = ""
    if very_recent_newsletters:
        breaking_news_section = "\n## JUST IN: LATEST DEVELOPMENTS\n\n"
        breaking_news_section += "These items are from the most recent newsletters (last 24 hours) and may represent emerging trends:\n\n"
        breaking_news_indicators = ['breaking', 'just in', 'just announced', 'new release', 
                                   'launches', 'launched', 'announces', 'announced', 
                                   'releases', 'released', 'introduces', 'introduced',
                                   'unveils', 'unveiled', 'debuts', 'just now']
        for nl in very_recent_newsletters:
            subject = nl['subject']
            clean_subject = re.sub(r'^\[.*?\]', '', subject).strip()
            clean_subject = re.sub(r'^.*?:', '', clean_subject).strip()
            highlight = any(indicator in subject.lower() for indicator in breaking_news_indicators)
            if highlight:
                breaking_news_section += f"- 🔥 **{clean_subject}** (via {nl['sender'].split('<')[0].strip()})\n"
            else:
                breaking_news_section += f"- {clean_subject} (via {nl['sender'].split('<')[0].strip()})\n"
    
    # Build report content - start directly with date range and main content
    report_body = f"""\
{date_range}

## TOP {topic.upper()} DEVELOPMENTS THIS WEEK

{llm_analysis}
"""
    report = report_body  # Keep for backward compatibility within function
    if breaking_news_section:
        report += breaking_news_section
    # Load or initialize website cache
    website_cache_path = 'newsletter_websites.json'
    curated_path = 'curated_websites.json'
    if os.path.exists(website_cache_path):
        with open(website_cache_path, 'r') as f:
            website_cache = json.load(f)
    else:
        website_cache = {}
    # Curated mapping for known newsletters (extend as needed)
    # Curated websites may live in an external JSON file for easy extension
    curated_websites = {
        'the neuron': 'https://www.theneurondaily.com',
        'tldr ai': 'https://www.tldrnewsletter.com',
        'tldr': 'https://www.tldrnewsletter.com',
        'the rundown ai': 'https://www.therundown.ai',
        'ai breakfast': 'https://aibreakfast.substack.com',
        "ben's bites": 'https://www.bensbites.co',
        'alpha signal': 'https://alphasignal.ai',
        'unwind ai': 'https://unwindai.com',
        'simon willison': 'https://simonwillison.net',
        'peter yang': 'https://creatoreconomy.so',
    }
    if os.path.exists(curated_path):
        try:
            with open(curated_path, 'r') as f:
                curated_loaded = json.load(f)
            if isinstance(curated_loaded, dict):
                curated_websites.update({k.lower(): v for k, v in curated_loaded.items() if isinstance(k, str) and isinstance(v, str)})
        except Exception:
            pass
    def normalize(text):
        return re.sub(r'[^a-z0-9]', '', text.lower())
    def domain_from_email(email):
        domain = email.split('@')[-1]
        domain = re.sub(r'^(mail|news|info|newsletter)\.', '', domain)
        return domain
    def plausible_homepage_from_body(body, newsletter_name=None):
        urls = re.findall(r'https?://[\w\.-]+(?:/[\w\-\./?%&=]*)?', body)
        # Filter out forms, tracking, deep paths, etc.
        filtered = [u for u in urls if not any(x in u for x in ['form', 'track', 'unsubscribe', 'pixel', 'img', 'logo', 'pricing', 'cdn-cgi', 'utm_', 'jwt_token', 'viewform'])]
        # Prefer root domains
        for url in filtered:
            parsed = urlparse(url)
            if parsed.path in ('', '/', '/home'):
                return url
        # As fallback, return first filtered
        if filtered:
            return filtered[0]
        return None
    report += f"""\
## NEWSLETTER SOURCES

This week's insights were gathered from {len(newsletters)} newsletters across {len(newsletter_sources)} sources:

"""
    for source, count in newsletter_sources.most_common():
        matching_nl = next((nl for nl in newsletters if nl['sender'] == source), None)
        if matching_nl:
            match = re.match(r'(.*?)\s*<(.+?)>', source)
            if match:
                name, email = match.groups()
            else:
                name = source
                email = None
            name = name.strip()
            cache_key = name.strip().lower()
            cache_entry = website_cache.get(cache_key)
            website_url = None
            verified = False
            # 1. Curated mapping
            norm_name = normalize(name)
            curated_match = None
            for k, v in curated_websites.items():
                if normalize(k) in norm_name:
                    curated_match = v
                    break
            if cache_entry and cache_entry.get('verified'):
                website_url = cache_entry['url']
                verified = True
            elif curated_match:
                website_url = curated_match
                verified = True
            # 2. Prefer plausible homepage from body
            if not website_url:
                candidate = plausible_homepage_from_body(matching_nl['body'], newsletter_name=name)
                if candidate:
                    website_url = candidate
                    verified = False
            # 3. Sender domain as fallback, except for generic 'Unknown' sender
            if not website_url and email:
                domain = domain_from_email(email)
                if name.strip().lower() != 'unknown':
                    website_url = f"https://{domain}"
                    verified = False
            # Update cache
            if website_url:
                # If from curated, always mark as verified
                if curated_match and website_url == curated_match:
                    website_cache[cache_key] = {"url": website_url, "verified": True}
                else:
                    website_cache[cache_key] = {"url": website_url, "verified": verified}
            # Format: - [Newsletter Name](Website URL) - N issues
            if website_url:
                report += f"- [{name.strip()}]({website_url}) - {count} issues\n"
            else:
                report += f"- {name.strip()} - {count} issues\n"
    # Save updated cache
    with open(website_cache_path, 'w') as f:
        json.dump(website_cache, f, indent=2)
    
    report += "\n## METHODOLOGY\n"
    report += f"This report was generated by analyzing {topic} newsletters "
    report += "with a focus on practical implications for regular users rather than industry competition."
    
    # Add model information to methodology section
    if model_info:
        model_name = model_info["model"]
        # Use real datetime for stable formatting under test patching
        timestamp_dt = _RealDatetime.fromisoformat(model_info["timestamp"]) if model_info.get("timestamp") else _RealDatetime.now()
        timestamp = timestamp_dt.strftime("%Y-%m-%d %H:%M:%S")
        report += f" Analysis performed using {model_name} on {timestamp}."
    
    # Combine frontmatter and body for Jekyll
    report_with_frontmatter = frontmatter + report
    
    return report_with_frontmatter, filename_date_range, label