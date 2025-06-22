import subprocess
import json
import time

def get_security_emails():
    # AppleScript to get security emails
    applescript = """
    tell application "Safari"
        activate
        delay 2
        
        -- Navigate to Gmail security search
        set URL of current tab of window 1 to "https://mail.google.com/mail/u/0/#search/security"
        delay 5
        
        -- Get emails from the page
        tell document 1
            set emails to do JavaScript "var emails = [];
            var elements = document.querySelectorAll('div[role=\"article\"]');
            for (var i = 0; i < elements.length; i++) {
                var element = elements[i];
                var subject = element.querySelector('div[role=\"heading\"]').textContent;
                var date = element.querySelector('span[role=\"link\"]').textContent;
                var snippet = element.querySelector('div[role=\"button\"]').textContent;
                emails.push({subject: subject, date: date, snippet: snippet});
            }
            JSON.stringify(emails);"
            return emails
        end tell
    end tell
    """
    
    try:
        # Run the AppleScript
        result = subprocess.run(['osascript', '-e', applescript], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            # Parse and sort emails
            emails = json.loads(result.stdout)
            emails.sort(key=lambda x: x["date"], reverse=True)
            
            # Print emails
            for email in emails:
                print(f"\n📧 {email['subject']}")
                print(f"📅 {email['date']}")
                print(f"📝 {email['snippet']}")
        else:
            print(f"Error: {result.stderr}")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    get_security_emails()
