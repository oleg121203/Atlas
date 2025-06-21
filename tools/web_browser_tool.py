import webbrowser
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def open_url(url: str) -> str:
    """
    Opens the specified URL in the default web browser.

    Args:
        url (str): The URL to open.

    Returns:
        str: A confirmation message indicating the action was attempted.
    """
    if not url.startswith('http://') and not url.startswith('https://'):
        logging.warning(f"URL '{url}' does not have a valid scheme. Prepending 'https://'.")
        url = f'https://{url}'

    try:
        logging.info(f"Attempting to open URL: {url}")
        webbrowser.open(url, new=2)  # new=2 opens in a new tab, if possible
        return f"Successfully requested to open URL: {url}"
    except Exception as e:
        logging.error(f"Failed to open URL {url}: {e}")
        return f"Error: Could not open URL {url}. Reason: {e}"

if __name__ == '__main__':
    # Example usage for standalone testing
    print("Testing Web Browser Tool...")
    test_url = "https://www.google.com"
    print(f"Opening test URL: {test_url}")
    result = open_url(test_url)
    print(result)

    print("\nTesting with a URL without a scheme...")
    test_url_no_scheme = "github.com"
    print(f"Opening test URL: {test_url_no_scheme}")
    result = open_url(test_url_no_scheme)
    print(result)
