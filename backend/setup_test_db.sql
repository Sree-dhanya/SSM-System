UPDATE users 
SET username = 'test_' || username,
    email = REPLACE(email, '@', '_test@');

UPDATE users 
SET hashed_password = '$2b$12$rzSJQ1/OZkgsXe2ZwB9N6OhjX4vTGcyzI8TNralXSmfN1TvnQ02hG'
WHERE username = 'test_admin';