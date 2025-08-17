# AI Newsletter Summarizer

The AI Newsletter Summarizer is a Python tool designed to automatically retrieve, analyze, and summarize AI-focused newsletters from a user's Gmail account. It distills key developments and actionable insights from multiple newsletters into a concise, easy-to-understand report targeted at regular users, rather than just AI experts.

## Features

- **Reliable newsletter fetching** - Sequential processing with robust retry logic and error handling
- **Resilient error handling** - Continues processing even if individual newsletters fail to fetch or parse
- **Robust HTML parsing** - Multiple fallback strategies ensure content extraction even from malformed emails
- Automatically fetches emails tagged with "ai-newsletter" from your Gmail account
- Extracts and analyzes content from multiple newsletter sources
- Identifies key topics and trends across newsletters using advanced LLM techniques
- Uses OpenRouter to route requests to Google Gemini 2.5 Flash (default), OpenAI GPT-4.1, or Anthropic's Claude 3.7 Sonnet for cost-efficient API usage and tracking
- Prioritizes recent content and breaking news (configurable)
- Outputs a markdown report with the top AI developments, why they matter, and actionable insights
- Includes links to newsletter sources and a brief methodology section
- **Modular codebase**: Authentication, fetching, LLM analysis, and reporting are in separate modules for easier maintenance and extension

## Requirements

- Python 3.11 (recommended) or 3.10-3.13 (also supported)
- Gmail account with newsletters tagged/labeled as `ai-newsletter`
- Google API credentials (`credentials.json`) - see setup instructions below
- **OpenRouter API key** (set as `OPENROUTER_API_KEY` environment variable) - required as the default API provider
- OpenAI API key (set as `OPENAI_API_KEY` environment variable) - only needed if not using OpenRouter
- Anthropic API key (set as `ANTHROPIC_API_KEY` environment variable) - only needed if not using OpenRouter

## Installation

1.  **Clone the repository**

    ```bash
    git clone https://github.com/saadiq/newsletter_summary.git
    cd newsletter_summary
    ```

2.  **Set up a virtual environment (Recommended)**

    ```bash
    # Use Python 3.11 (recommended)
    python3.11 -m venv venv
    source venv/bin/activate  # On macOS/Linux
    # venv\Scripts\activate  # On Windows
    ```

3.  **Install dependencies**

    ```bash
    pip install --upgrade pip setuptools wheel
    pip install -r requirements.txt
    ```

4.  **Set up Google OAuth credentials**

    You can set up Gmail API credentials using either the Google Cloud Console (web UI) or the gcloud CLI.

    ### Option A: Using Google Cloud Console (Web UI)
    
    - Go to the [Google Cloud Console](https://console.cloud.google.com/)
    - Create a new project or select an existing one
    - Enable the **Gmail API** for your project
    - Go to "Credentials", click "Create Credentials", and select "OAuth client ID"
    - Choose "Desktop application" as the application type
    - Download the credentials JSON file
    - **Rename and save the downloaded file as `credentials.json`** in the project's root directory

    ### Option B: Using gcloud CLI
    
    If you have the gcloud CLI installed:
    
    ```bash
    # Authenticate with Google Cloud
    gcloud auth login
    
    # Create a new project (or use existing)
    gcloud projects create my-newsletter-summarizer --name="Newsletter Summarizer"
    gcloud config set project my-newsletter-summarizer
    
    # Enable Gmail API
    gcloud services enable gmail.googleapis.com
    
    # Create OAuth 2.0 credentials for desktop app
    # Note: This creates the OAuth consent screen and client
    gcloud auth application-default login --scopes=https://www.googleapis.com/auth/gmail.readonly
    
    # Download the credentials
    # You'll need to create OAuth client ID through the Console for desktop apps
    # as gcloud doesn't directly support creating desktop OAuth clients
    ```
    
    After using gcloud to set up the project and enable APIs, you'll still need to:
    1. Go to [Google Cloud Console](https://console.cloud.google.com/)
    2. Navigate to "APIs & Services" > "Credentials"
    3. Click "Create Credentials" > "OAuth client ID"
    4. Select "Desktop app" and download the JSON
    5. Save as `credentials.json` in the project directory
    
    Note: The gcloud commands help with project setup and API enabling, but OAuth client creation for desktop apps still requires the Console.

5.  **Get an OpenRouter API key**

    - Sign up at [OpenRouter](https://openrouter.ai/) (if you don't have an account).
    - Obtain an API key from your account dashboard.

6.  **Create a `.env.local` file**

    Create a file named `.env.local` in the project directory and add your API keys:

    ```dotenv
    # Required - default API provider
    OPENROUTER_API_KEY=your_openrouter_api_key_here
    
    # Optional - OpenRouter configuration
    USE_OPENROUTER=true
    OPENROUTER_COST_LOG=openrouter_costs.json
    
    # Optional - only needed if bypassing OpenRouter with USE_OPENROUTER=false
    ANTHROPIC_API_KEY=your_anthropic_api_key_here
    OPENAI_API_KEY=your_openai_api_key_here
    ```
    *(Note: Ensure this file is included in your `.gitignore` if you plan to commit the code)*

7.  **Validate your configuration**

    Before running the main application, validate all your settings:

    ```bash
    python config_validator.py
    ```

    This will check:
    - API keys are properly set
    - Gmail credentials are valid
    - Newsletter websites JSON is properly formatted
    - No duplicate or invalid URLs in the cache

## Quick Start

After installation:

```bash
# Validate configuration
python config_validator.py

# Run with defaults (7 days, Google Gemini via OpenRouter)
python main.py

# Use Claude instead
python main.py --llm-provider claude

# Use OpenAI GPT-4.1 instead
python main.py --llm-provider openai

# Analyze last 14 days
python main.py --days 14
```

## Usage

1.  **Setup Gmail Label**

    In your Gmail account, create a label named exactly `ai-newsletter`. Apply this label to all the AI newsletters you want the script to process.

2.  **Activate the virtual environment**

    ```bash
    source venv/bin/activate  # On macOS/Linux
    # venv\Scripts\activate  # On Windows
    ```

3.  **Run the tool**

    **The entry point is `main.py`**:

    ```bash
    python main.py
    ```

    By default, this analyzes newsletters from the past 7 days using OpenRouter to connect to Google Gemini 2.5 Flash. See Command-line Options below to customize.

    **Example: Use Claude 3.7 Sonnet instead of Google Gemini (default):**
    ```bash
    python main.py --llm-provider claude
    ```
    
    **Example: Use OpenAI GPT-4.1 instead of default:**
    ```bash
    python main.py --llm-provider openai
    ```
    
    **Example: Use a specific custom OpenRouter model:**
    ```bash
    python main.py --model google/gemini-2.5-flash-preview:thinking
    ```
    
    **Example: Specify the number of topics to extract and analyze:**
    ```bash
    python main.py --num-topics 7
    ```

4.  **First-time Authentication**

    The *very first time* you run the tool, it will open a browser window. You'll need to:
    - Log in to the Google account associated with the Gmail inbox you want to analyze.
    - Grant the tool permission to **view your email messages and settings** (this is the `gmail.readonly` scope).
    After successful authentication, the tool will create a `token.json` file to store the authorization credentials, so you won't need to authenticate via the browser on subsequent runs (unless the token expires or is revoked).

5.  **View the Results**

    The tool will output progress messages to the console. Once finished, it will generate a markdown file in the `docs/_posts/` directory with Jekyll-compatible naming: `YYYY-MM-DD-label-summary-Xd.md` (where X is the number of days covered by the report). The file includes Jekyll frontmatter for GitHub Pages integration. Open this file to view your summarized report, or visit your GitHub Pages site after pushing the changes.

### Output Directory

By default, reports are saved to `docs/_posts/` for GitHub Pages integration. You can customize this:

- CLI flag (overrides default):
  ```bash
  python main.py --output /custom/path
  ```
- Environment variable (overrides default if no CLI flag specified):
  ```bash
  export NEWSLETTER_SUMMARY_OUTPUT_DIR=/custom/path
  ```
- To use current directory (old behavior):
  ```bash
  python main.py --output .
  ```

### Mock Data for Testing

For development or testing, you can inject mock newsletter data by setting the `NEWSLETTER_SUMMARY_MOCK_DATA` environment variable to a JSON array of newsletter objects. This will bypass Gmail fetching:

```bash
export NEWSLETTER_SUMMARY_MOCK_DATA='[{"subject": "Test Subject", "date": "2024-01-01", "sender": "sender@example.com", "body": "Test body."}]'
```

## Command-line Options

You can modify the tool's behavior using these optional flags:

-   `--days N`: Specify the number of past days to retrieve emails from.
    ```bash
    python main.py --days 14
    ```
    (Default: `7`)

-   `--label LABEL`: Specify the Gmail label to filter newsletters (default: `ai-newsletter`).
    ```bash
    python main.py --label my-custom-label
    ```

-   `--no-label`: Do not use any Gmail label as a search criterion (useful if you want to search by other criteria like sender).
    ```bash
    python main.py --no-label --from-email newsletter@example.com
    ```

-   `--from-email EMAIL`: Only include emails from the specified sender.
    ```bash
    python main.py --from-email newsletter@example.com
    ```

-   `--to-email EMAIL`: Only include emails sent to the specified recipient.
    ```bash
    python main.py --to-email yourname@gmail.com
    ```

-   `--llm-provider PROVIDER`: Choose between `google` (default), `claude`, or `openai`.
    ```bash
    python main.py --llm-provider claude  # Use Claude
    python main.py --llm-provider openai  # Use OpenAI GPT-4.1
    ```

-   `--model MODEL`: Specify a custom OpenRouter model to use (overrides --llm-provider).
    ```bash
    python main.py --model google/gemini-2.5-flash-preview:thinking
    ```
    This allows using any model available on OpenRouter.

-   `--num-topics N`: Specify the number of topics to extract and summarize (default: 10).
    ```bash
    python main.py --num-topics 7
    ```

-   `--no-prioritize-recent`: Disable higher weighting for recent newsletters.
    ```bash
    python main.py --no-prioritize-recent
    ```

-   `--no-breaking-news-section`: Disable the separate "Just In" section for latest developments.
    ```bash
    python main.py --no-breaking-news-section
    ```

-   `-h` / `--help`: Show all available command-line options and usage examples.

## Model Presets

The tool uses different models depending on whether you're using OpenRouter (default) or direct API calls:

### OpenRouter Models (Default)
When `USE_OPENROUTER=true` (default), the presets map to these OpenRouter models:

- `claude` → `anthropic/claude-sonnet-4`
- `openai` → `openai/gpt-4.1-mini` 
- `google` → `google/gemini-2.5-flash`

### Direct API Models (Fallback)
When `USE_OPENROUTER=false`, the presets map to these direct API models:

- `claude` → `claude-3-7-sonnet-20250219`
- `openai` → `gpt-4.1-2025-04-14`
- `google` → `gemini-2.5-flash-preview`

You can also use the `--model` parameter to specify any custom OpenRouter model directly, which overrides the preset mappings.

## OpenRouter Integration

This project uses [OpenRouter](https://openrouter.ai) by default for all LLM API calls, providing:

1. Competitive pricing
2. Detailed usage tracking
3. Access to both Claude and OpenAI models through a single API

To check your OpenRouter setup:
```bash
python verify_openrouter.py
```

To analyze request costs:
```bash
python analyze_costs.py
```

## Approach

The tool uses a single, streamlined approach to generating summaries:

### Direct-to-LLM Analysis
- Sends newsletter content directly to the LLM in one step
- LLM identifies the most significant topics and generates summaries simultaneously
- Produces coherent, ranked topics with actionable insights for regular users

## Modular Architecture

The codebase is organized into the following modules for clarity and maintainability:

- `auth.py` — Gmail authentication
- `fetch.py` — Email fetching
- `llm.py` — LLM analysis
- `report.py` — Report generation
- `main.py` — Entry point (run this file to use your tool)

## Customization

For more advanced modifications:

-   To modify the number of key topics extracted, adjust the `num_topics` argument.
-   To change the direct-LLM prompt or model, edit the `analyze_newsletters_unified` function in `llm.py`.
-   To customize the final report format or content, modify the `generate_report` function in `report.py`.

## Newsletter Website Cache & Review Workflow

The tool caches detected newsletter websites for each source and marks them as **verified** or **unverified**:
- **Verified:** Trusted and used for future runs.
- **Unverified:** Used as a fallback, but will be replaced if a better guess or curated mapping is found.
- **Curated mapping:** Always takes precedence and is always trusted.

### How to Review and Confirm Newsletter Websites

1. **After running the tool**, review the detected websites for accuracy:

    ```bash
    python review_newsletter_websites.py
    ```

    For each unverified entry, you can:
    - `[a]ccept` to mark as verified
    - `[e]dit` to correct the website and mark as verified
    - `[d]elete` to remove the entry (it will be re-guessed next run)
    - `[s]kip` to leave it unverified for now

2. **Why review?**
    - Ensures your report always links to the correct main site for each newsletter.
    - Prevents bad guesses (e.g., tracking links, forms) from persisting in your reports.
    - Lets you maintain high-quality, human-verified source links.

3. **How to extend the curated mapping:**
    - Create or edit `curated_websites.json` (key: newsletter name, value: url). Entries override guesses and are treated as verified.

## Performance & Reliability

### Recent Improvements (August 2025)

- **Reliable newsletter fetching** with automatic retry logic and exponential backoff
- **Graceful error handling** - individual newsletter failures don't crash the entire process
- **Enhanced HTML parsing** with multiple fallback strategies for malformed content
- **Detailed error reporting** with troubleshooting tips for common issues

### Reliability Features

- The tool fetches newsletters sequentially with automatic retry on failures
- Built-in exponential backoff prevents rate limiting issues
- Failed fetches are reported but don't stop processing of successful ones
- For very large volumes (50+ newsletters), consider using `--days` to limit the date range

## Troubleshooting

### Common Issues

-   **Authentication Failed**: 
    - Check that `credentials.json` exists in the project directory
    - Delete `token.json` and re-authenticate if the token has expired
    - Ensure Gmail API is enabled in Google Cloud Console

-   **No Newsletters Found**:
    - Verify the Gmail label exists and is spelled correctly (default: `ai-newsletter`)
    - Check if there are emails within the specified date range (`--days`)
    - Try using `--no-label` with `--from-email` to search by sender instead

-   **Rate Limiting**:
    - The tool automatically handles rate limits with retry logic
    - If persistent, wait a few minutes and try again

-   **HTML Parsing Errors**:
    - The tool now has multiple fallback strategies and will extract text even from malformed HTML
    - Check the report for `[Plain text extraction]` or `[Fallback text extraction]` markers

-   **NumPy Build Errors / Python Version:** 
    - Use Python 3.11 (recommended) or 3.10-3.13
    - Some scientific packages may have issues with the latest Python versions

-   **OpenRouter API Issues**: 
    - Run `python verify_openrouter.py` to check your setup
    - If problems persist, set `USE_OPENROUTER=false` in `.env.local` to use direct API calls

### Debug Mode

For detailed error traces, set the DEBUG environment variable:

```bash
export DEBUG=1
python main.py
```

## Testing

The project includes comprehensive test coverage:

- `test_fetch_api.py`: Unit tests for email fetching, retry logic, and error handling
- `test_e2e_cli.py`: End-to-end tests for the CLI workflow and report generation
- `test_llm.py`: Tests for LLM integration and OpenRouter functionality
- `test_report.py`: Tests for report generation and formatting
- `test_utils.py`: Tests for HTML parsing and text extraction
- `test_auth.py`: Tests for Gmail authentication
- `test_config_validator.py`: Tests for configuration validation

To run all tests:

```bash
pytest
```

To run specific test files:

```bash
pytest test_fetch_api.py  # Test fetching with retry logic
pytest test_e2e_cli.py    # Test full workflow
```

To run with coverage:

```bash
pytest --cov=. --cov-report=html
```

## GitHub Pages Automated Publishing

This project includes full GitHub Actions automation for weekly newsletter summaries published to GitHub Pages.

### Setting Up GitHub Pages

1. **Enable GitHub Pages**
   - Go to your repository on GitHub
   - Navigate to Settings → Pages
   - Under "Source", select "Deploy from a branch"
   - Choose `gh-pages` branch and `/ (root)` folder
   - Click Save

2. **Prepare Gmail Secrets**
   
   First, generate properly formatted secrets from your local credentials:
   
   ```bash
   python prepare_github_secrets.py
   ```
   
   This creates a `github_secrets.txt` file with your credentials properly formatted for GitHub.

3. **Add GitHub Secrets**
   
   Go to your repository → Settings → Secrets and variables → Actions, then add these repository secrets:
   
   - **GMAIL_CREDENTIALS**: Copy the entire JSON content from `github_secrets.txt` (the part between the dashed lines for GMAIL_CREDENTIALS)
   - **GMAIL_TOKEN**: Copy the entire JSON content from `github_secrets.txt` (the part between the dashed lines for GMAIL_TOKEN)
   - **OPENROUTER_API_KEY**: Your OpenRouter API key
   
   **Important**: Make sure you're adding "Repository secrets" not "Environment secrets"

4. **Delete Sensitive Files**
   
   After adding secrets to GitHub, delete the temporary file:
   
   ```bash
   rm github_secrets.txt
   ```

### GitHub Actions Workflow

The included workflow (`.github/workflows/generate-summary.yml`) automatically:

- **Runs weekly**: Every Sunday at 10 AM UTC
- **Fetches newsletters**: From the past 7 days with the `ai-newsletter` label
- **Generates summaries**: Using your configured LLM provider
- **Commits reports**: To `docs/_posts/` with proper Jekyll frontmatter
- **Publishes to GitHub Pages**: Automatically deploys to your site

### Manual Workflow Runs

You can also trigger the workflow manually:

1. Go to Actions tab in your repository
2. Select "Generate Newsletter Summary"
3. Click "Run workflow"
4. Optionally customize:
   - **days**: Number of days to look back (default: 7)
   - **label**: Gmail label to filter (default: ai-newsletter)

### Viewing Your Published Site

After the workflow runs successfully:

1. Your site will be available at: `https://[username].github.io/newsletter_summary/`
2. Reports are automatically organized by date
3. The site includes:
   - Dark/light mode toggle
   - Filter by newsletter labels
   - Clean, professional styling
   - Mobile-responsive design

### Troubleshooting GitHub Actions

**Common Issues:**

1. **"Permission denied" errors**
   - Already fixed in the workflow with proper permissions
   - If issues persist, check Settings → Actions → General → Workflow permissions

2. **"Invalid JSON" in secrets**
   - Use `prepare_github_secrets.py` to ensure proper formatting
   - Secrets must be valid JSON without any extra characters

3. **"No newsletters found"**
   - Check that your Gmail token hasn't expired
   - Verify the label exists in your Gmail account
   - Try running locally first to ensure authentication works

4. **Memory/Segmentation faults**
   - The workflow is optimized for GitHub Actions with:
     - Sequential processing to ensure reliability
     - Memory limits to prevent crashes
     - Automatic retry logic with exponential backoff

### Customizing the Workflow

Edit `.github/workflows/generate-summary.yml` to:

- Change schedule (modify the cron expression)
- Adjust default parameters
- Add additional steps
- Configure different deployment targets

### Local Testing Before Deployment

Test the full automation locally:

```bash
# Generate a report with commit flag
python main.py --commit

# Push to trigger GitHub Pages build
git push origin main
```

## Contributing

Contributions are welcome! Feel free to submit a Pull Request.

## License

This project is available under the MIT License.