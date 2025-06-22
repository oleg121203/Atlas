tell application "Safari"
    activate
    delay 2
    
    -- Navigate to Gmail security search
    set URL of current tab of window 1 to "https://mail.google.com/mail/u/0/#search/security"
    delay 5 -- Wait for page to load
    
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
        emails;"
        return emails
    end tell
end tell
