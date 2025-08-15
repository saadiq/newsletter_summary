# Setting Up GitHub Secrets for Newsletter Summarizer

To enable the GitHub Actions workflow to access Gmail and generate summaries, you need to set up the following secrets in your repository.

## Required Secrets

### 1. OPENROUTER_API_KEY
Your OpenRouter API key for LLM access.

### 2. GMAIL_CREDENTIALS
The contents of your `credentials.json` file. To get this:

```bash
# Copy the entire contents of credentials.json
cat credentials.json | pbcopy  # macOS
# or
cat credentials.json | xclip -selection clipboard  # Linux
```

Then paste it as the secret value.

### 3. GMAIL_TOKEN
The contents of your `token.json` file. To get this:

```bash
# Copy the entire contents of token.json
cat token.json | pbcopy  # macOS
# or
cat token.json | xclip -selection clipboard  # Linux
```

Then paste it as the secret value.

## How to Add Secrets

1. Go to your repository on GitHub
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add each secret with the exact name above
5. Paste the corresponding value

## Important Notes

- The `token.json` file contains your Gmail OAuth token and may expire
- If the token expires, you'll need to:
  1. Run the script locally to refresh: `python main.py --days 1`
  2. Update the `GMAIL_TOKEN` secret with the new token content
- Make sure to copy the ENTIRE file contents, including all brackets and quotes

## Testing

After setting up secrets, you can test the workflow:
1. Go to **Actions** tab in your repository
2. Select **Generate Newsletter Summary**
3. Click **Run workflow**
4. Check the logs for any errors

## Troubleshooting

If Gmail authentication fails in GitHub Actions:
1. Check that both secrets are properly set (no extra spaces or missing characters)
2. Verify your token hasn't expired by running locally
3. Enable debug logging in the workflow to see detailed errors
4. Consider using a service account instead of OAuth for more stable automation