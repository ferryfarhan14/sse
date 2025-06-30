from src.models.page import Page, AllowedDomain, db
from src.crawler import WebCrawler
from typing import List, Dict
import logging
from urllib.parse import urlparse

class SearchIndexer:
    def __init__(self, app):
        """
        Initialize search indexer
        
        Args:
            app: Flask application instance
        """
        self.app = app
        self.logger = logging.getLogger(__name__)
    
    def add_allowed_domain(self, domain: str) -> bool:
        """
        Add a domain to allowed domains list
        
        Args:
            domain: Domain to add (e.g., 'example.com')
            
        Returns:
            True if added successfully, False if already exists
        """
        try:
            with self.app.app_context():
                existing = AllowedDomain.query.filter_by(domain=domain.lower()).first()
                if existing:
                    if not existing.is_active:
                        existing.is_active = True
                        db.session.commit()
                        self.logger.info(f"Reactivated domain: {domain}")
                        return True
                    else:
                        self.logger.info(f"Domain already exists: {domain}")
                        return False
                
                new_domain = AllowedDomain(domain=domain.lower())
                db.session.add(new_domain)
                db.session.commit()
                self.logger.info(f"Added new allowed domain: {domain}")
                return True
                
        except Exception as e:
            self.logger.error(f"Error adding domain {domain}: {str(e)}")
            return False
    
    def get_allowed_domains(self) -> List[str]:
        """Get list of active allowed domains"""
        try:
            with self.app.app_context():
                domains = AllowedDomain.query.filter_by(is_active=True).all()
                return [domain.domain for domain in domains]
        except Exception as e:
            self.logger.error(f"Error getting allowed domains: {str(e)}")
            return []
    
    def index_page(self, page_data: Dict) -> bool:
        """
        Index a single page
        
        Args:
            page_data: Dictionary containing page data
            
        Returns:
            True if indexed successfully
        """
        try:
            with self.app.app_context():
                # Check if page already exists
                existing_page = Page.query.filter_by(url=page_data['url']).first()
                
                if existing_page:
                    # Update existing page
                    existing_page.title = page_data.get('title', '')
                    existing_page.content = page_data.get('content', '')
                    existing_page.description = page_data.get('description', '')
                    existing_page.keywords = page_data.get('keywords', '')
                    existing_page.is_active = True
                    self.logger.info(f"Updated existing page: {page_data['url']}")
                else:
                    # Create new page
                    new_page = Page(
                        url=page_data['url'],
                        title=page_data.get('title', ''),
                        content=page_data.get('content', ''),
                        description=page_data.get('description', ''),
                        keywords=page_data.get('keywords', ''),
                        domain=page_data['domain']
                    )
                    db.session.add(new_page)
                    self.logger.info(f"Added new page: {page_data['url']}")
                
                db.session.commit()
                return True
                
        except Exception as e:
            self.logger.error(f"Error indexing page {page_data.get('url', 'unknown')}: {str(e)}")
            db.session.rollback()
            return False
    
    def index_pages(self, pages_data: List[Dict]) -> int:
        """
        Index multiple pages
        
        Args:
            pages_data: List of page data dictionaries
            
        Returns:
            Number of successfully indexed pages
        """
        success_count = 0
        
        for page_data in pages_data:
            if self.index_page(page_data):
                success_count += 1
        
        self.logger.info(f"Successfully indexed {success_count}/{len(pages_data)} pages")
        return success_count
    
    def crawl_and_index(self, urls: List[str]) -> int:
        """
        Crawl URLs and index the content
        
        Args:
            urls: List of URLs to crawl and index
            
        Returns:
            Number of successfully indexed pages
        """
        allowed_domains = self.get_allowed_domains()
        
        if not allowed_domains:
            self.logger.warning("No allowed domains configured")
            return 0
        
        crawler = WebCrawler(allowed_domains)
        crawled_data = crawler.crawl_urls(urls)
        
        return self.index_pages(crawled_data)
    
    def search_pages(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Search for pages matching the query
        
        Args:
            query: Search query
            limit: Maximum number of results to return
            
        Returns:
            List of matching page dictionaries
        """
        try:
            with self.app.app_context():
                # Simple text search in title, content, and description
                search_term = f"%{query}%"
                
                pages = Page.query.filter(
                    db.and_(
                        Page.is_active == True,
                        db.or_(
                            Page.title.ilike(search_term),
                            Page.content.ilike(search_term),
                            Page.description.ilike(search_term),
                            Page.keywords.ilike(search_term)
                        )
                    )
                ).limit(limit).all()
                
                results = []
                for page in pages:
                    page_dict = page.to_dict()
                    # Truncate content for search results
                    if page_dict['content'] and len(page_dict['content']) > 300:
                        page_dict['content'] = page_dict['content'][:300] + '...'
                    results.append(page_dict)
                
                self.logger.info(f"Found {len(results)} results for query: {query}")
                return results
                
        except Exception as e:
            self.logger.error(f"Error searching for query '{query}': {str(e)}")
            return []
    
    def get_stats(self) -> Dict:
        """Get indexing statistics"""
        try:
            with self.app.app_context():
                total_pages = Page.query.filter_by(is_active=True).count()
                total_domains = AllowedDomain.query.filter_by(is_active=True).count()
                
                # Get pages per domain
                domain_stats = db.session.query(
                    Page.domain,
                    db.func.count(Page.id).label('count')
                ).filter_by(is_active=True).group_by(Page.domain).all()
                
                return {
                    'total_pages': total_pages,
                    'total_domains': total_domains,
                    'pages_per_domain': {domain: count for domain, count in domain_stats}
                }
                
        except Exception as e:
            self.logger.error(f"Error getting stats: {str(e)}")
            return {
                'total_pages': 0,
                'total_domains': 0,
                'pages_per_domain': {}
            }

