import sqlite3
import json
import feedparser
import datetime
from flask import current_app, g
from .database import get_db
from .content_extractor import ContentExtractor

class Feed:
    @staticmethod
    def get_all():
        db = get_db()
        feeds = db.execute('SELECT * FROM feed ORDER BY title').fetchall()
        return [dict(feed) for feed in feeds]
    
    @staticmethod
    def get_by_id(feed_id):
        db = get_db()
        feed = db.execute('SELECT * FROM feed WHERE id = ?', (feed_id,)).fetchone()
        if feed is None:
            return None
        return dict(feed)
    
    @staticmethod
    def create(title, url, description=None):
        db = get_db()
        try:
            cursor = db.execute(
                'INSERT INTO feed (title, url, description) VALUES (?, ?, ?)',
                (title, url, description)
            )
            feed_id = cursor.lastrowid
            db.commit()
            return feed_id
        except sqlite3.IntegrityError:
            return None
    
    @staticmethod
    def update(feed_id, title, url, description=None):
        db = get_db()
        try:
            db.execute(
                'UPDATE feed SET title = ?, url = ?, description = ?, last_updated = CURRENT_TIMESTAMP WHERE id = ?',
                (title, url, description, feed_id)
            )
            db.commit()
            return True
        except sqlite3.Error:
            return False
    
    @staticmethod
    def delete(feed_id):
        db = get_db()
        db.execute('DELETE FROM feed WHERE id = ?', (feed_id,))
        db.commit()
        return True
    
    @staticmethod
    def refresh(feed_id=None):
        """Fetch new articles from one or all feeds"""
        db = get_db()
        
        if feed_id:
            feeds = [Feed.get_by_id(feed_id)]
            if not feeds[0]:
                return False
        else:
            feeds = Feed.get_all()
        
        for feed in feeds:
            try:
                # Parse the feed
                parsed_feed = feedparser.parse(feed['url'])
                
                # Update feed info if needed
                if parsed_feed.feed.get('title') and parsed_feed.feed.title != feed['title']:
                    Feed.update(feed['id'], parsed_feed.feed.title, feed['url'], 
                               parsed_feed.feed.get('description', feed['description']))
                
                # Process entries
                for entry in parsed_feed.entries:
                    # Check if article already exists
                    existing = db.execute(
                        'SELECT id FROM article WHERE url = ?', (entry.link,)
                    ).fetchone()
                    
                    if existing:
                        continue
                    
                    # Get published date
                    published = None
                    for date_field in ['published_parsed', 'updated_parsed', 'created_parsed']:
                        if hasattr(entry, date_field) and getattr(entry, date_field):
                            time_struct = getattr(entry, date_field)
                            published = datetime.datetime(*time_struct[:6])
                            break
                    
                    # Get content
                    content = None
                    if hasattr(entry, 'content') and entry.content:
                        content = entry.content[0].value
                    elif hasattr(entry, 'summary'):
                        content = entry.summary
                    
                    # Get author
                    author = None
                    if hasattr(entry, 'author'):
                        author = entry.author
                    
                    # Insert article
                    db.execute(
                        'INSERT INTO article (feed_id, title, url, content, author, published_at) VALUES (?, ?, ?, ?, ?, ?)',
                        (feed['id'], entry.title, entry.link, content, author, published)
                    )
                
                db.commit()
            except Exception as e:
                current_app.logger.error(f"Error refreshing feed {feed['url']}: {str(e)}")
                continue
        
        return True

class Article:
    @staticmethod
    def get_all(page=1, per_page=20, feed_id=None, unread_only=False):
        db = get_db()
        params = []
        query = '''
            SELECT a.*, f.title as feed_title
            FROM article a
            JOIN feed f ON a.feed_id = f.id
            WHERE 1=1
        '''
        
        if feed_id:
            query += ' AND a.feed_id = ?'
            params.append(feed_id)
        
        if unread_only:
            query += ' AND a.read = 0'
        
        query += ' ORDER BY a.published_at DESC LIMIT ? OFFSET ?'
        params.extend([per_page, (page - 1) * per_page])
        
        articles = db.execute(query, params).fetchall()
        return [dict(article) for article in articles]
    
    @staticmethod
    def get_by_id(article_id):
        db = get_db()
        article = db.execute(
            'SELECT a.*, f.title as feed_title FROM article a JOIN feed f ON a.feed_id = f.id WHERE a.id = ?',
            (article_id,)
        ).fetchone()
        
        if article is None:
            return None
        
        return dict(article)
    
    @staticmethod
    def mark_as_read(article_id, read=True):
        db = get_db()
        db.execute(
            'UPDATE article SET read = ? WHERE id = ?',
            (1 if read else 0, article_id)
        )
        db.commit()
        return True

    @staticmethod
    def fetch_full_content(article_id):
        """Fetch and store the full content of an article"""
        db = get_db()
        article = db.execute(
            'SELECT * FROM article WHERE id = ?',
            (article_id,)
        ).fetchone()
        
        if article is None:
            return None, "Article not found"
        
        article_dict = dict(article)
        
        # Check if we already have full content
        if article_dict.get('full_content'):
            return article_dict, None
        
        # Extract content from the article URL
        _, content, error = ContentExtractor.extract_content(article_dict['url'])
        
        if error:
            return article_dict, error
        
        # Update the article with the full content
        db.execute(
            'UPDATE article SET full_content = ? WHERE id = ?',
            (content, article_id)
        )
        db.commit()
        
        # Return the updated article
        article_dict['full_content'] = content
        return article_dict, None

class SyncConfig:
    @staticmethod
    def get_by_key(sync_key):
        db = get_db()
        config = db.execute(
            'SELECT * FROM sync_config WHERE sync_key = ?',
            (sync_key,)
        ).fetchone()
        
        if config is None:
            return None
        
        result = dict(config)
        result['config_data'] = json.loads(result['config_data'])
        return result
    
    @staticmethod
    def create_or_update(sync_key, config_data):
        db = get_db()
        
        # Check if config exists
        existing = db.execute(
            'SELECT id FROM sync_config WHERE sync_key = ?',
            (sync_key,)
        ).fetchone()
        
        config_json = json.dumps(config_data)
        
        if existing:
            db.execute(
                'UPDATE sync_config SET config_data = ?, updated_at = CURRENT_TIMESTAMP WHERE sync_key = ?',
                (config_json, sync_key)
            )
        else:
            db.execute(
                'INSERT INTO sync_config (sync_key, config_data) VALUES (?, ?)',
                (sync_key, config_json)
            )
        
        db.commit()
        return True
    
    @staticmethod
    def export_feeds():
        """Export all feeds in OPML format for backup/sync"""
        feeds = Feed.get_all()
        opml_data = {
            'version': '1.0',
            'feeds': feeds
        }
        return json.dumps(opml_data)
    
    @staticmethod
    def import_feeds(opml_data):
        """Import feeds from OPML data"""
        db = get_db()
        try:
            data = json.loads(opml_data)
            feeds = data.get('feeds', [])
            
            for feed in feeds:
                # Check if feed exists
                existing = db.execute(
                    'SELECT id FROM feed WHERE url = ?',
                    (feed['url'],)
                ).fetchone()
                
                if existing:
                    continue
                
                # Add new feed
                Feed.create(feed['title'], feed['url'], feed.get('description'))
            
            db.commit()
            return True
        except Exception as e:
            current_app.logger.error(f"Error importing feeds: {str(e)}")
            return False
