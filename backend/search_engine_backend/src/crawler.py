import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urlunparse
import time
import logging
from typing import List, Dict, Optional
import re

class WebCrawler:
    def __init__(self, allowed_domains: List[str], delay: float = 1.0):
        """
        Initialize web crawler
        
        Args:
            allowed_domains: List of domains that are allowed to be crawled
            delay: Delay between requests in seconds
        """
        self.allowed_domains = [domain.lower() for domain in allowed_domains]
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'SimpleSearchEngine/1.0 (+http://localhost:5000)'
        })
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def is_allowed_domain(self, url: str) -> bool:
        """Check if URL domain is in allowed domains list"""
        try:
            domain = urlparse(url).netloc.lower()
            return any(domain == allowed or domain.endswith('.' + allowed) 
                      for allowed in self.allowed_domains)
        except:
            return False
    
    def clean_url(self, url: str) -> str:
        """Clean URL by removing fragments and unnecessary parameters"""
        parsed = urlparse(url)
        # Remove fragment
        cleaned = urlunparse((
            parsed.scheme, parsed.netloc, parsed.path,
            parsed.params, parsed.query, ''
        ))
        return cleaned
    
    def extract_text_content(self, soup: BeautifulSoup) -> str:
        """Extract clean text content from HTML"""
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # Get text and clean it
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def extract_metadata(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract metadata from HTML"""
        metadata = {
            'title': '',
            'description': '',
            'keywords': ''
        }
        
        # Extract title
        title_tag = soup.find('title')
        if title_tag:
            metadata['title'] = title_tag.get_text().strip()
        
        # Extract meta description
        desc_tag = soup.find('meta', attrs={'name': 'description'})
        if desc_tag:
            metadata['description'] = desc_tag.get('content', '').strip()
        
        # Extract meta keywords
        keywords_tag = soup.find('meta', attrs={'name': 'keywords'})
        if keywords_tag:
            metadata['keywords'] = keywords_tag.get('content', '').strip()
        
        return metadata
    
    def crawl_page(self, url: str) -> Optional[Dict]:
        """
        Crawl a single page and extract its content
        
        Returns:
            Dictionary with page data or None if failed
        """
        if not self.is_allowed_domain(url):
            self.logger.warning(f"Domain not allowed: {url}")
            return None
        
        try:
            self.logger.info(f"Crawling: {url}")
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # Check if content is HTML
            content_type = response.headers.get('content-type', '').lower()
            if 'text/html' not in content_type:
                self.logger.warning(f"Not HTML content: {url}")
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract content and metadata
            content = self.extract_text_content(soup)
            metadata = self.extract_metadata(soup)
            
            # Get domain
            domain = urlparse(url).netloc.lower()
            
            page_data = {
                'url': self.clean_url(url),
                'title': metadata['title'],
                'content': content,
                'description': metadata['description'],
                'keywords': metadata['keywords'],
                'domain': domain
            }
            
            # Add delay between requests
            time.sleep(self.delay)
            
            return page_data
            
        except requests.RequestException as e:
            self.logger.error(f"Request failed for {url}: {str(e)}")
            return None
        except Exception as e:
            self.logger.error(f"Error crawling {url}: {str(e)}")
            return None
    
    def crawl_urls(self, urls: List[str]) -> List[Dict]:
        """
        Crawl multiple URLs
        
        Args:
            urls: List of URLs to crawl
            
        Returns:
            List of successfully crawled page data
        """
        results = []
        
        for url in urls:
            page_data = self.crawl_page(url)
            if page_data:
                results.append(page_data)
        
        return results
    
    def discover_links(self, url: str, max_depth: int = 1) -> List[str]:
        """
        Discover links from a page (basic implementation)
        
        Args:
            url: Starting URL
            max_depth: Maximum depth to crawl (not implemented yet)
            
        Returns:
            List of discovered URLs
        """
        if not self.is_allowed_domain(url):
            return []
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            links = []
            
            for link in soup.find_all('a', href=True):
                href = link['href']
                full_url = urljoin(url, href)
                
                if self.is_allowed_domain(full_url):
                    cleaned_url = self.clean_url(full_url)
                    if cleaned_url not in links:
                        links.append(cleaned_url)
            
            return links
            
        except Exception as e:
            self.logger.error(f"Error discovering links from {url}: {str(e)}")
            return []

