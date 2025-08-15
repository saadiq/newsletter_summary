---
layout: default
title: About
---

# About Newsletter Summaries

This site hosts automated summaries of newsletters generated using AI language models. The summaries are created by the [Newsletter Summarizer](https://github.com/saadiq/newsletter_summary) tool.

## How It Works

1. **Email Collection**: The tool fetches newsletters from Gmail based on specified labels
2. **AI Analysis**: Newsletters are analyzed using LLMs (Google Gemini, OpenAI GPT-4, or Claude)
3. **Summary Generation**: Key topics and insights are extracted and formatted
4. **Publication**: Reports are automatically published to this GitHub Pages site

## Features

- **Parallel Processing**: Fetches multiple newsletters simultaneously for faster processing
- **Resilient Architecture**: Continues processing even if individual newsletters fail
- **Multiple AI Models**: Supports various LLMs through OpenRouter
- **Automatic Publishing**: Reports can be auto-committed and pushed to GitHub Pages

## Configuration

The tool is highly configurable:
- Choose different Gmail labels to summarize different newsletter categories
- Select from multiple AI models for analysis
- Customize the number of topics to extract
- Control date ranges and filtering options

## Source Code

The full source code is available on [GitHub](https://github.com/saadiq/newsletter_summary).

## Privacy Note

All summaries are generated from newsletters that have been explicitly labeled for processing. No personal or sensitive information is included in the published summaries.