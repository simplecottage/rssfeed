DROP TABLE IF EXISTS feed;
DROP TABLE IF EXISTS article;
DROP TABLE IF EXISTS sync_config;

CREATE TABLE feed (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  url TEXT UNIQUE NOT NULL,
  description TEXT,
  last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE article (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  feed_id INTEGER NOT NULL,
  title TEXT NOT NULL,
  url TEXT UNIQUE NOT NULL,
  content TEXT,
  full_content TEXT,
  author TEXT,
  published_at TIMESTAMP,
  read BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (feed_id) REFERENCES feed (id) ON DELETE CASCADE
);

CREATE TABLE sync_config (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  sync_key TEXT UNIQUE NOT NULL,
  config_data TEXT NOT NULL,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for faster queries
CREATE INDEX idx_feed_id ON article (feed_id);
CREATE INDEX idx_read ON article (read);
CREATE INDEX idx_published_at ON article (published_at);
