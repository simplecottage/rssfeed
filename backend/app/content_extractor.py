import requests
import html2text
from bs4 import BeautifulSoup
from readability import Document
from flask import current_app

class ContentExtractor:
    @staticmethod
    def extract_content(url):
        """
        Extract the main content from a webpage URL
        Returns tuple of (title, content, error)
        """
        try:
            # Set a proper user agent to avoid being blocked
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            # Fetch the page
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Use readability to extract the main content
            doc = Document(response.text)
            title = doc.title()
            
            # Get the main content
            content = doc.summary()
            
            # Clean up the HTML
            soup = BeautifulSoup(content, 'html.parser')
            
            # Remove unnecessary elements
            for element in soup.select('script, style, iframe, nav, footer, .ad, .advertisement, .banner'):
                element.decompose()
            
            # Fix relative URLs in images and links
            base_url = '/'.join(url.split('/')[:3])  # Get domain (http[s]://domain.com)
            
            for img in soup.find_all('img', src=True):
                src = img['src']
                if src.startswith('/'):
                    img['src'] = base_url + src
                elif not src.startswith(('http://', 'https://')):
                    # Handle relative paths
                    img['src'] = url.rsplit('/', 1)[0] + '/' + src
            
            for a in soup.find_all('a', href=True):
                href = a['href']
                if href.startswith('/'):
                    a['href'] = base_url + href
                elif not href.startswith(('http://', 'https://')):
                    # Handle relative paths
                    a['href'] = url.rsplit('/', 1)[0] + '/' + href
                
                # Open external links in new tab
                if href.startswith(('http://', 'https://')):
                    a['target'] = '_blank'
                    a['rel'] = 'noopener noreferrer'
            
            # Convert back to string
            clean_html = str(soup)
            
            # Optional: Convert to markdown if needed
            # markdown = html2text.HTML2Text()
            # markdown.ignore_links = False
            # markdown.body_width = 0
            # markdown_content = markdown.handle(clean_html)
            
            return title, clean_html, None
            
        except requests.RequestException as e:
            current_app.logger.error(f"Error fetching URL {url}: {str(e)}")
            return None, None, f"Failed to fetch article: {str(e)}"
        except Exception as e:
            current_app.logger.error(f"Error extracting content from {url}: {str(e)}")
            return None, None, f"Failed to extract article content: {str(e)}"

    @staticmethod
    def is_paywall_or_login_required(content):
        """
        Basic check to detect paywalls or login walls
        """
        paywall_indicators = [
            'subscribe', 'subscription', 'paywall', 'sign in', 'sign up', 
            'login', 'register', 'premium', 'account', 'paid', 'subscribe now'
        ]
        
        content_lower = content.lower()
        
        # Look for paywall indicators
        indicators_found = [ind for ind in paywall_indicators if ind in content_lower]
        
        # If multiple indicators are found, it might be a paywall
        return len(indicators_found) >= 3
