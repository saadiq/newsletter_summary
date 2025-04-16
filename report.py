import re
from collections import Counter
import datetime

def generate_report(newsletters, topics, llm_analysis, days):
    """Generate a final report with key insights."""
    newsletter_sources = Counter([nl['sender'] for nl in newsletters])
    newsletter_dates = []
    newsletter_with_dates = []
    for i, nl in enumerate(newsletters):
        try:
            from email.utils import parsedate_to_datetime
            date_obj = parsedate_to_datetime(nl['date'])
            newsletter_dates.append(date_obj)
            newsletter_with_dates.append((i, nl, date_obj))
        except Exception as e:
            print(f"Warning: Could not parse date '{nl['date']}': {str(e)}")
    if newsletter_dates:
        earliest_date = min(newsletter_dates)
        latest_date = max(newsletter_dates)
        run_time = datetime.datetime.now()
        date_range = f"## {earliest_date.strftime('%B %d')} to {latest_date.strftime('%B %d, %Y, %H:%M')} (summary run at {run_time.strftime('%Y-%m-%d %H:%M')})"
        filename_date_range = f"{earliest_date.strftime('%Y%m%d')}_to_{run_time.strftime('%Y%m%d_%H%M')}"
    else:
        earliest_date = datetime.datetime.now() - datetime.timedelta(days=days)
        run_time = datetime.datetime.now()
        date_range = f"## Week of {earliest_date.strftime('%B %d')} to {run_time.strftime('%B %d, %Y, %H:%M')} (summary run at {run_time.strftime('%Y-%m-%d %H:%M')})"
        filename_date_range = f"{earliest_date.strftime('%Y%m%d')}_to_{run_time.strftime('%Y%m%d_%H%M')}"
    very_recent_newsletters = []
    cutoff_date = latest_date - datetime.timedelta(days=1)
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
    report = f"""
# AI NEWSLETTER SUMMARY
{date_range}

## TOP 5 AI DEVELOPMENTS THIS WEEK

{llm_analysis}
"""
    if breaking_news_section:
        report += breaking_news_section
    report += f"""
## NEWSLETTER SOURCES

This week's insights were gathered from {len(newsletters)} newsletters across {len(newsletter_sources)} sources:

"""
    for source, count in newsletter_sources.most_common():
        matching_nl = next((nl for nl in newsletters if nl['sender'] == source), None)
        if matching_nl:
            match = re.match(r'(.*?)\s*<(.+?)>', source)
            if match:
                name, email = match.groups()
                domain = email.split('@')[-1]
                web_link = f"https://www.{domain}"
                report += f"- [{name.strip()}](mailto:{email}) ([Website]({web_link})) - {count} issues\n"
            else:
                if '@' in source:
                    domain = source.split('@')[-1]
                    web_link = f"https://www.{domain}"
                    report += f"- [{source}](mailto:{source}) ([Website]({web_link})) - {count} issues\n"
                else:
                    report += f"- [{source}](mailto:{source}) - {count} issues\n"
    report += "\n## METHODOLOGY\n"
    report += "This report was generated by analyzing AI newsletters tagged in Gmail. "
    report += "Key topics were identified using frequency analysis and natural language processing, "
    report += "with a focus on practical implications for regular users rather than industry competition."
    return report, filename_date_range 