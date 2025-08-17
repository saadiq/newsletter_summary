# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI Newsletter Summarizer - A Python CLI tool that fetches AI-focused newsletters from Gmail, analyzes them with LLMs (via OpenRouter by default), and generates concise summary reports for regular users.

**Recent Improvements (Aug 2025):**
- Robust error handling with retry logic and graceful degradation
- Enhanced HTML parsing with multiple fallback strategies
- Better user feedback with detailed error messages and troubleshooting tips

## Common Development Commands

```bash
# Setup environment (Python 3.11 recommended)
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For testing

# Run the application (saves to docs/_posts by default)
python main.py [options]

# Save to current directory instead
python main.py --output .

# Run all tests
pytest

# Run specific test file
pytest test_fetch_api.py
pytest test_e2e_cli.py

# Run specific test
pytest test_fetch_api.py::test_get_ai_newsletters_success

# Verify OpenRouter setup
python verify_openrouter.py

# Analyze API costs
python analyze_costs.py

# Review newsletter website mappings
python review_newsletter_websites.py

# Validate configuration
python config_validator.py
```

## High-Level Architecture

The codebase follows a modular architecture with clear separation of concerns:

### Core Flow
1. **Authentication** (`auth.py`) - Handles Gmail OAuth using Google API credentials with error recovery
2. **Email Fetching** (`fetch.py`) - Retrieves newsletters sequentially with automatic retry logic
3. **LLM Analysis** (`llm.py`) - Sends content to LLMs (OpenRouter/direct APIs) for analysis
4. **Report Generation** (`report.py`) - Creates markdown reports with summaries and insights

### Key Architectural Decisions

- **OpenRouter as Default**: All LLM calls route through OpenRouter by default for cost efficiency and tracking
- **Provider Abstraction**: Supports multiple LLM providers (OpenAI, Anthropic, Google) with consistent interface
- **Newsletter Website Caching**: Maintains `newsletter_websites.json` to cache and verify newsletter sources
- **Mock Data Support**: E2E tests and development can use `NEWSLETTER_SUMMARY_MOCK_DATA` env var
- **Cost Tracking**: OpenRouter usage logged to `openrouter_costs.json` for analysis
- **Resilient Architecture**: Retry decorators with exponential backoff for API calls
- **Graceful Degradation**: Individual failures don't crash the entire process

### Environment Configuration

Required `.env.local` file:
```
OPENROUTER_API_KEY=your_key_here  # Required
USE_OPENROUTER=true               # Default behavior
# Direct API keys only needed if USE_OPENROUTER=false
ANTHROPIC_API_KEY=your_key
OPENAI_API_KEY=your_key
```

### Model Selection Logic

The `--llm-provider` flag maps to specific models (default is `google`):
- With OpenRouter: `google` → `google/gemini-2.5-flash` (default), `claude` → `anthropic/claude-sonnet-4`, `openai` → `openai/gpt-4.1-mini`
- Direct APIs: `google` → `gemini-2.5-flash-preview`, `claude` → `claude-3-7-sonnet-20250219`, `openai` → `gpt-4.1-2025-04-14`
- Custom models via `--model` parameter override these presets

### Testing Strategy

- **Unit Tests** (`test_fetch_api.py`): Mock Gmail API responses, test filtering logic, retry mechanisms
- **E2E Tests** (`test_e2e_cli.py`): Run full CLI with mock data, verify report generation
- Tests use monkeypatching and environment variables to avoid external dependencies
- Mock `tqdm` with context manager pattern for progress tracking tests

### Key Files to Understand Cross-Module Behavior

1. **main.py** orchestrates the entire flow with enhanced error handling and user feedback
2. **llm.py** contains the unified analysis prompt and model routing logic
3. **report.py** handles both report generation and newsletter website detection/caching
4. **fetch.py** implements sequential fetching with retry logic and failure tracking
5. **utils.py** provides robust HTML parsing with multiple fallback strategies
6. **config_validator.py** validates all configuration files and environment variables

### Configuration Validation

The project includes comprehensive configuration validation via `config_validator.py`:
- **Environment Variables**: Validates API keys, file paths, and OpenRouter settings
- **JSON Files**: Validates `newsletter_websites.json` structure, URLs, and detects duplicates/tracking URLs
- **Credentials**: Validates Gmail OAuth configuration files
- Run `python config_validator.py` to check all configuration before running the main application
### Development Best Practices

- **Error Handling**: Always implement retry logic for external API calls
- **User Feedback**: Provide clear error messages with troubleshooting steps
- **Performance**: Implement retry logic for all external API calls
- **Testing**: Update tests when changing function signatures or behavior
- **Commits**: Use the code-committer agent for well-crafted commit messages and pushes

### Common Debugging Tips

1. **Gmail API Issues**: Check `token.json` expiry, delete and re-authenticate if needed
2. **Rate Limiting**: The app handles rate limits with exponential backoff automatically
3. **HTML Parsing Failures**: Check `utils.py` fallback methods, app will extract text even from malformed HTML
4. **Rate Limiting Issues**: The app handles rate limits with exponential backoff automatically
5. **Mock Data Testing**: Set `NEWSLETTER_SUMMARY_MOCK_DATA` env var with JSON array