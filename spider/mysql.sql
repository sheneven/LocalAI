-- 新闻主表
CREATE TABLE news_info (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    url VARCHAR(2048) UNIQUE NOT NULL,
    title TEXT NOT NULL,
    summary TEXT,
    origin VARCHAR(64),
    author VARCHAR(64),
    sentiment_score FLOAT,
    published_time VARCHAR(64),
    create_time DATETIME,
    update_time DATETIME,
    del_flag VARCHAR(1) DEFAULT '0',
    comment VARCHAR(128),
    source_url VARCHAR(2048)
);

-- 新闻标签表
CREATE TABLE news_label (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    news_id INT PRIMARY KEY,
    label  VARCHAR(16)
);
-- 用户兴趣标签表
CREATE TABLE user_interests (
    user_id INT PRIMARY KEY,
    interests JSON ARRAY NOT NULL DEFAULT ''
);