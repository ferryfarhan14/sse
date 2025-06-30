from flask import Blueprint, request, jsonify
from src.indexer import SearchIndexer
from src.models.page import AllowedDomain, Page, db
import logging

search_bp = Blueprint('search', __name__)
logger = logging.getLogger(__name__)

# Global indexer instance (will be initialized in main.py)
indexer = None

def init_search_routes(app):
    """Initialize search routes with app context"""
    global indexer
    indexer = SearchIndexer(app)

@search_bp.route('/search', methods=['GET'])
def search():
    """
    Search for pages
    
    Query parameters:
    - q: search query (required)
    - limit: maximum results (optional, default 10)
    """
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify({
                'error': 'Query parameter "q" is required'
            }), 400
        
        limit = request.args.get('limit', 10, type=int)
        if limit > 50:
            limit = 50  # Maximum limit
        
        results = indexer.search_pages(query, limit)
        
        return jsonify({
            'query': query,
            'results': results,
            'total': len(results)
        })
        
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        return jsonify({
            'error': 'Internal server error'
        }), 500

@search_bp.route('/domains', methods=['GET'])
def get_domains():
    """Get list of allowed domains"""
    try:
        domains = indexer.get_allowed_domains()
        return jsonify({
            'domains': domains,
            'total': len(domains)
        })
        
    except Exception as e:
        logger.error(f"Get domains error: {str(e)}")
        return jsonify({
            'error': 'Internal server error'
        }), 500

@search_bp.route('/domains', methods=['POST'])
def add_domain():
    """
    Add a new allowed domain
    
    JSON body:
    - domain: domain name (required)
    """
    try:
        data = request.get_json()
        if not data or 'domain' not in data:
            return jsonify({
                'error': 'Domain is required'
            }), 400
        
        domain = data['domain'].strip().lower()
        if not domain:
            return jsonify({
                'error': 'Domain cannot be empty'
            }), 400
        
        success = indexer.add_allowed_domain(domain)
        
        if success:
            return jsonify({
                'message': f'Domain {domain} added successfully',
                'domain': domain
            })
        else:
            return jsonify({
                'message': f'Domain {domain} already exists',
                'domain': domain
            })
        
    except Exception as e:
        logger.error(f"Add domain error: {str(e)}")
        return jsonify({
            'error': 'Internal server error'
        }), 500

@search_bp.route('/crawl', methods=['POST'])
def crawl_urls():
    """
    Crawl and index URLs
    
    JSON body:
    - urls: list of URLs to crawl (required)
    """
    try:
        data = request.get_json()
        if not data or 'urls' not in data:
            return jsonify({
                'error': 'URLs list is required'
            }), 400
        
        urls = data['urls']
        if not isinstance(urls, list) or not urls:
            return jsonify({
                'error': 'URLs must be a non-empty list'
            }), 400
        
        # Validate URLs
        valid_urls = []
        for url in urls:
            if isinstance(url, str) and url.strip():
                valid_urls.append(url.strip())
        
        if not valid_urls:
            return jsonify({
                'error': 'No valid URLs provided'
            }), 400
        
        indexed_count = indexer.crawl_and_index(valid_urls)
        
        return jsonify({
            'message': f'Successfully indexed {indexed_count}/{len(valid_urls)} pages',
            'indexed_count': indexed_count,
            'total_urls': len(valid_urls)
        })
        
    except Exception as e:
        logger.error(f"Crawl error: {str(e)}")
        return jsonify({
            'error': 'Internal server error'
        }), 500

@search_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get indexing statistics"""
    try:
        stats = indexer.get_stats()
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Stats error: {str(e)}")
        return jsonify({
            'error': 'Internal server error'
        }), 500

@search_bp.route('/pages', methods=['GET'])
def get_pages():
    """
    Get list of indexed pages
    
    Query parameters:
    - domain: filter by domain (optional)
    - limit: maximum results (optional, default 20)
    - offset: pagination offset (optional, default 0)
    """
    try:
        domain = request.args.get('domain', '').strip()
        limit = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        if limit > 100:
            limit = 100  # Maximum limit
        
        query = Page.query.filter_by(is_active=True)
        
        if domain:
            query = query.filter_by(domain=domain.lower())
        
        pages = query.offset(offset).limit(limit).all()
        total = query.count()
        
        results = []
        for page in pages:
            page_dict = page.to_dict()
            # Truncate content for listing
            if page_dict['content'] and len(page_dict['content']) > 200:
                page_dict['content'] = page_dict['content'][:200] + '...'
            results.append(page_dict)
        
        return jsonify({
            'pages': results,
            'total': total,
            'limit': limit,
            'offset': offset
        })
        
    except Exception as e:
        logger.error(f"Get pages error: {str(e)}")
        return jsonify({
            'error': 'Internal server error'
        }), 500

