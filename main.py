from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import re

# Set maximum recursion depth
MAX_DEPTH = 3
visited_urls = set()
emails_found = {}  # Dictionary to store emails with the first URL where they were found

# Define a blacklist of domains to skip
BLACKLIST = ["linkedin.com"]

def extract_emails(text):
    """Extract emails using regex."""
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    return re.findall(email_pattern, text)

def extract_all_links(html, base_url):
    """Extract all <a> tags from the HTML and resolve relative URLs."""
    soup = BeautifulSoup(html, 'lxml')
    links = []

    # Find all <a> tags with href attributes
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        # Resolve relative URLs to absolute URLs
        absolute_url = urljoin(base_url, href)
        links.append(absolute_url)

    return links

def is_blacklisted(url):
    """Check if the URL is blacklisted."""
    return any(blacklisted in url for blacklisted in BLACKLIST)

def is_same_domain(url, base_url):
    """Check if the URL belongs to the same domain."""
    return urlparse(url).netloc == urlparse(base_url).netloc

def traverse_website(driver, url, base_url, depth=0):
    """Recursively traverse the website and extract links."""
    if depth > MAX_DEPTH or url in visited_urls or is_blacklisted(url):
        return

    print(f"Visiting: {url}")
    visited_urls.add(url)

    try:
        driver.get(url)
        time.sleep(0.01)  # Allow the page to load
    except Exception as e:
        print(f"Failed to load {url}: {e}")
        return

    # Extract emails from the page
    emails = extract_emails(driver.page_source)
    for email in emails:
        # Store the first URL where the email was found
        if email not in emails_found:
            emails_found[email] = url

    print(f"Emails found on {url}: {emails}")

    # Extract all links from the HTML, resolving relative URLs
    links = extract_all_links(driver.page_source, url)

    for link in links:
        if link.startswith("http") and is_same_domain(link, base_url) and link not in visited_urls:
            try:
                # Recursively visit the link
                traverse_website(driver, link, base_url, depth + 1)
            except Exception as e:
                print(f"Error visiting {link}: {e}")

if __name__ == "__main__":
    # Set up the Selenium WebDriver (ensure ChromeDriver is installed and in PATH)
    driver = webdriver.Chrome()

    # Start with the initial URL
    start_url = "https://www.webai.com/"

    # Begin the recursive traversal
    traverse_website(driver, start_url, start_url)

    # Print all emails found with the first URL they were found at
    print("\nAll emails found with their first occurrence:")
    for email, url in emails_found.items():
        print(f"{email} found at {url}")

    # Quit the driver
    driver.quit()
