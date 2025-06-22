# Gmail API Setup Guide

This guide will help you set up Gmail API integration for Atlas to enable real email searching and analysis.

## Prerequisites

- Google account with Gmail
- Python 3.7 or higher
- Required Python packages (see installation section)

## Step 1: Install Required Packages

First, install the required Google API packages:

```bash
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

## Step 2: Create Google Cloud Project

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Gmail API:
   - Go to "APIs & Services" > "Library"
   - Search for "Gmail API"
   - Click on it and press "Enable"

## Step 3: Create OAuth 2.0 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth 2.0 Client IDs"
3. Choose "Desktop application" as the application type
4. Give it a name (e.g., "Atlas Gmail Integration")
5. Click "Create"
6. Download the credentials file (JSON format)

## Step 4: Configure Atlas

1. Place the downloaded credentials file in one of these locations:
   - `credentials.json` (in Atlas root directory)
   - `gmail_credentials.json` (in Atlas root directory)
   - `config/credentials.json`
   - `~/.atlas/gmail_credentials.json`

2. The file should be named `credentials.json` and contain your OAuth 2.0 credentials.

## Step 5: First Authentication

When you first run Atlas with Gmail integration:

1. Atlas will attempt to authenticate with Gmail
2. A browser window will open asking you to authorize the application
3. Sign in with your Google account
4. Grant the requested permissions:
   - Read Gmail messages
   - Modify Gmail messages (if needed)
5. A `token.json` file will be created automatically for future use

## Step 6: Test the Integration

You can test the Gmail integration by running:

```bash
python tools/gmail_tool.py
```

This will:
1. Test authentication
2. Search for security emails
3. Display results

## Security Considerations

- Keep your `credentials.json` and `token.json` files secure
- Don't commit these files to version control
- The token file contains sensitive authentication data
- Consider using environment variables for production deployments

## Troubleshooting

### Common Issues

1. **"Gmail API libraries not available"**
   - Install the required packages: `pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client`

2. **"Gmail credentials not found"**
   - Ensure the credentials file is in one of the expected locations
   - Check that the file is named correctly and contains valid JSON

3. **"Authentication failed"**
   - Delete the `token.json` file and try again
   - Ensure you have the correct permissions enabled in Google Cloud Console
   - Check that your Google account has Gmail enabled

4. **"Gmail API request failed"**
   - Check your internet connection
   - Ensure the Gmail API is enabled in your Google Cloud project
   - Verify your OAuth 2.0 credentials are correct

### API Quotas

- Gmail API has daily quotas for requests
- Free tier: 1 billion queries per day
- If you hit quotas, consider implementing rate limiting

## Usage Examples

Once configured, Atlas can:

1. **Search for security emails:**
   ```
   "Find all security-related emails in my Gmail"
   ```

2. **Search with specific criteria:**
   ```
   "Search Gmail for emails from Google about account security"
   ```

3. **Get email content:**
   ```
   "Read the content of specific security emails"
   ```

## Advanced Configuration

### Custom Search Queries

You can modify the search queries in `tools/gmail_tool.py`:

```python
def search_security_emails(self, days_back: int = 30) -> Dict[str, Any]:
    # Modify these queries to match your needs
    security_queries = [
        f"{date_filter} (security OR password OR login OR account)",
        f"{date_filter} from:(noreply@accounts.google.com)",
        # Add your custom queries here
    ]
```

### Scopes Configuration

The tool uses these Gmail API scopes:
- `https://www.googleapis.com/auth/gmail.readonly` - Read emails
- `https://www.googleapis.com/auth/gmail.modify` - Modify emails (if needed)

You can modify the scopes in `tools/gmail_tool.py` if you need different permissions.

## Support

If you encounter issues:

1. Check the Atlas logs for detailed error messages
2. Verify your Google Cloud Console configuration
3. Test the Gmail API directly using the Google API Explorer
4. Check the [Gmail API documentation](https://developers.google.com/gmail/api)

## Next Steps

After setting up Gmail API:

1. Atlas will be able to perform real email searches
2. The hierarchical planning system will use actual Gmail data
3. You'll get real email content and metadata in search results
4. Browser automation will work with actual Safari/Gmail interaction

This transforms Atlas from a simulation to a real email analysis tool! 