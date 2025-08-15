import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

from dotenv import load_dotenv
load_dotenv('.env.local')

import argparse
import datetime
from auth import authenticate_gmail
from fetch import get_ai_newsletters
from utils import clean_body
from llm import analyze_newsletters_unified
from report import generate_report
import json

def get_default_model_name(provider):
    """Return the actual model name based on the provider."""
    model_map = {
        'claude': "claude-3-7-sonnet-20250219",
        'openai': "gpt-4.1-2025-04-14",
        'google': "gemini-2.5-flash-preview"
    }
    return model_map.get(provider, "unknown model")

def main():
    parser = argparse.ArgumentParser(description='Summarize AI newsletters from Gmail.')
    parser.add_argument('--days', type=int, default=7, 
                        help='Number of days to look back for newsletters (default: 7)')
    parser.add_argument('--prioritize-recent', action='store_true',
                        help='Give higher weight to more recent newsletters (default: enabled)')
    parser.add_argument('--no-prioritize-recent', dest='prioritize_recent', action='store_false',
                        help='Do not give higher weight to more recent newsletters')
    parser.add_argument('--breaking-news-section', action='store_true',
                        help='Add a separate "Just In" section for latest newsletters (default: enabled)')
    parser.add_argument('--no-breaking-news-section', dest='breaking_news_section', action='store_false',
                        help='Do not add a separate "Just In" section')
    parser.add_argument('--llm-provider', choices=['claude', 'openai', 'google'], default='openai',
                        help='LLM provider for summarization: claude (Claude 3.7 Sonnet), openai (GPT-4.1), or google (Gemini 2.0 Flash)')
    parser.add_argument('--model', type=str, default=None,
                        help='Specify a custom OpenRouter model (e.g., "google/gemini-2.5-flash-preview:thinking") overriding the provider selection')
    parser.add_argument('--label', type=str, default='ai-newsletter',
                        help='Gmail label to filter newsletters (default: ai-newsletter)')
    parser.add_argument('--no-label', action='store_true',
                        help='Do not use any Gmail label as a search criteria (overrides --label)')
    parser.add_argument('--from-email', type=str, default=None,
                        help='Only include emails from this sender email address (optional)')
    parser.add_argument('--to-email', type=str, default=None,
                        help='Only include emails sent to this recipient email address (optional)')
    parser.add_argument('--num-topics', type=int, default=10,
                        help='Number of topics to extract and summarize (default: 10)')
    parser.add_argument('--output', type=str, default=None,
                        help='Output directory for the report (overrides NEWSLETTER_SUMMARY_OUTPUT_DIR)')
    parser.set_defaults(prioritize_recent=True, breaking_news_section=True)
    args = parser.parse_args()
    try:
        print("Authenticating with Gmail...")
        try:
            service = authenticate_gmail()
        except Exception as auth_error:
            print(f"\nAuthentication failed: {str(auth_error)}")
            print("\nTroubleshooting tips:")
            print("1. Check that credentials.json exists in the project directory")
            print("2. Delete token.json and re-authenticate if needed")
            print("3. Ensure Gmail API is enabled in Google Cloud Console")
            return
        label_arg = None if args.no_label else args.label
        print(f"Retrieving AI newsletters from the past {args.days} days... (label: {label_arg if label_arg else 'none'})")
        mock_data_env = os.environ.get("NEWSLETTER_SUMMARY_MOCK_DATA")
        if mock_data_env:
            newsletters = json.loads(mock_data_env)
        else:
            newsletters = get_ai_newsletters(
                service,
                days=args.days,
                label=label_arg,
                from_email=args.from_email,
                to_email=args.to_email
            )
        successful_count = len([n for n in newsletters if 'error' not in n])
        print(f"Found {len(newsletters)} newsletters (successfully fetched: {successful_count}).")
        
        if not newsletters:
            print("\nNo newsletters found. Possible reasons:")
            print(f"1. No emails with label '{label_arg}' in the last {args.days} days")
            print("2. Gmail API rate limit reached (try again later)")
            print("3. Network connectivity issues")
            return
        
        if successful_count == 0:
            print("\nAll newsletter fetches failed. Please check:")
            print("1. Your internet connection")
            print("2. Gmail API permissions")
            print("3. Try running again (temporary API issues)")
            return
        
        # Direct LLM approach - combined topic extraction and summarization
        if args.model:
            print(f"Using custom OpenRouter model: {args.model}")
        else:
            print(f"Using direct LLM approach with {args.llm_provider} to extract and summarize {args.num_topics} topics...")
        
        llm_analysis, topics = analyze_newsletters_unified(
            newsletters, 
            num_topics=args.num_topics,
            provider=args.llm_provider,
            model=args.model
        )
        
        print(f"Identified and analyzed {len(topics)} topics")
        
        # Construct model_info dictionary
        model_info = {
            "provider": args.llm_provider,
            "model": args.model if args.model else get_default_model_name(args.llm_provider),
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        print("Generating report...")
        if not args.breaking_news_section:
            def generate_report_without_breaking(newsletters, topics, llm_analysis, days, model_info):
                report, filename = generate_report(newsletters, topics, llm_analysis, days, model_info)
                import re
                report = re.sub(r'\n## JUST IN: LATEST DEVELOPMENTS\n\n.*?\n\n## ', '\n\n## ', report, flags=re.DOTALL)
                return report, filename
            
            report, filename_date_range = generate_report_without_breaking(newsletters, topics, llm_analysis, args.days, model_info)
        else:
            report, filename_date_range = generate_report(newsletters, topics, llm_analysis, args.days, model_info)
        
        report_filename = f"ai_newsletter_summary_{filename_date_range}.md"
        output_dir = args.output or os.environ.get("NEWSLETTER_SUMMARY_OUTPUT_DIR", "")
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            report_filename = os.path.join(output_dir, report_filename)
        with open(report_filename, 'w') as f:
            f.write(report)
        print(f"Report saved to {report_filename}")
    except ImportError as e:
        print(f"\nMissing dependency: {str(e)}")
        print("Please install required packages: pip install -r requirements.txt")
    except FileNotFoundError as e:
        print(f"\nFile not found: {str(e)}")
        print("Ensure credentials.json exists in the project directory")
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")
        print("\nFor debugging, you can:")
        print("1. Check the .env.local file for correct API keys")
        print("2. Run 'python config_validator.py' to validate configuration")
        print("3. Try with fewer days using --days flag")
        import traceback
        if os.environ.get('DEBUG'):
            traceback.print_exc()

if __name__ == "__main__":
    main()