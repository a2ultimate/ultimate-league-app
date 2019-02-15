INSERT INTO news_article (title, type, content, created, published, updated)
SELECT pybb_topic.name, 'html', pybb_post.body_html, pybb_post.created, pybb_post.created, pybb_post.created
FROM pybb_post
JOIN pybb_topic ON pybb_topic.id = pybb_post.topic_id
JOIN pybb_forum ON pybb_forum.id = pybb_topic.forum_id
WHERE pybb_forum.name = 'Announcements';
