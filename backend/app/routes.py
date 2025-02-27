from flask import Blueprint, request, jsonify, current_app
import json
import uuid
from .models import Feed, Article, SyncConfig

def register_routes(app):
    # Feed routes
    @app.route('/api/feeds', methods=['GET'])
    def get_feeds():
        feeds = Feed.get_all()
        return jsonify(feeds)
    
    @app.route('/api/feeds/<int:feed_id>', methods=['GET'])
    def get_feed(feed_id):
        feed = Feed.get_by_id(feed_id)
        if feed is None:
            return jsonify({'error': 'Feed not found'}), 404
        return jsonify(feed)
    
    @app.route('/api/feeds', methods=['POST'])
    def create_feed():
        data = request.get_json()
        if not data or not data.get('url') or not data.get('title'):
            return jsonify({'error': 'URL and title are required'}), 400
        
        feed_id = Feed.create(
            data['title'], 
            data['url'], 
            data.get('description')
        )
        
        if feed_id is None:
            return jsonify({'error': 'Feed already exists or invalid URL'}), 400
        
        # Refresh the feed to fetch articles
        Feed.refresh(feed_id)
        
        return jsonify({'id': feed_id}), 201
    
    @app.route('/api/feeds/<int:feed_id>', methods=['PUT'])
    def update_feed(feed_id):
        data = request.get_json()
        if not data or not data.get('url') or not data.get('title'):
            return jsonify({'error': 'URL and title are required'}), 400
        
        success = Feed.update(
            feed_id,
            data['title'], 
            data['url'], 
            data.get('description')
        )
        
        if not success:
            return jsonify({'error': 'Failed to update feed'}), 400
        
        return jsonify({'success': True})
    
    @app.route('/api/feeds/<int:feed_id>', methods=['DELETE'])
    def delete_feed(feed_id):
        Feed.delete(feed_id)
        return jsonify({'success': True})
    
    @app.route('/api/feeds/refresh', methods=['POST'])
    def refresh_feeds():
        feed_id = request.args.get('feed_id', type=int)
        success = Feed.refresh(feed_id)
        
        if not success:
            return jsonify({'error': 'Failed to refresh feeds'}), 400
        
        return jsonify({'success': True})
    
    # Article routes
    @app.route('/api/articles', methods=['GET'])
    def get_articles():
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        feed_id = request.args.get('feed_id', type=int)
        unread_only = request.args.get('unread_only', 'false').lower() == 'true'
        
        articles = Article.get_all(page, per_page, feed_id, unread_only)
        return jsonify(articles)
    
    @app.route('/api/articles/<int:article_id>', methods=['GET'])
    def get_article(article_id):
        article = Article.get_by_id(article_id)
        if article is None:
            return jsonify({'error': 'Article not found'}), 404
        return jsonify(article)
    
    @app.route('/api/articles/<int:article_id>/read', methods=['PUT'])
    def mark_article_read(article_id):
        read = request.args.get('read', 'true').lower() == 'true'
        Article.mark_as_read(article_id, read)
        return jsonify({'success': True})
    
    # Sync routes
    @app.route('/api/sync/key', methods=['GET'])
    def get_sync_key():
        # Generate a new sync key
        sync_key = str(uuid.uuid4())
        return jsonify({'sync_key': sync_key})
    
    @app.route('/api/sync/<sync_key>', methods=['GET'])
    def get_sync_data(sync_key):
        config = SyncConfig.get_by_key(sync_key)
        if config is None:
            return jsonify({'error': 'Sync key not found'}), 404
        return jsonify(config['config_data'])
    
    @app.route('/api/sync/<sync_key>', methods=['POST'])
    def update_sync_data(sync_key):
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        SyncConfig.create_or_update(sync_key, data)
        return jsonify({'success': True})
    
    @app.route('/api/export', methods=['GET'])
    def export_feeds():
        opml_data = SyncConfig.export_feeds()
        return jsonify({'data': opml_data})
    
    @app.route('/api/import', methods=['POST'])
    def import_feeds():
        data = request.get_json()
        if not data or not data.get('data'):
            return jsonify({'error': 'No data provided'}), 400
        
        success = SyncConfig.import_feeds(data['data'])
        if not success:
            return jsonify({'error': 'Failed to import feeds'}), 400
        
        return jsonify({'success': True})
    
    # Health check route
    @app.route('/health', methods=['GET'])
    def health():
        return jsonify({'status': 'ok'})

    @app.route('/api/articles/<int:article_id>/full-content', methods=['GET'])
    def get_article_full_content(article_id):
        article, error = Article.fetch_full_content(article_id)
        
        if error:
            return jsonify({'error': error}), 400
        
        if article is None:
            return jsonify({'error': 'Article not found'}), 404
        
        return jsonify(article)
