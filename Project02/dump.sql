USE music_streaming;

CREATE TABLE ADMIN (
    Aidx INT AUTO_INCREMENT PRIMARY KEY, 
    Aid VARCHAR(10) UNIQUE NOT NULL,     
    Aname VARCHAR(10) NOT NULL,         
    Apwd VARCHAR(20) NOT NULL 
);

CREATE TABLE USER (
    Uidx INT AUTO_INCREMENT PRIMARY KEY, 
    Uid VARCHAR(10) UNIQUE NOT NULL,     
    Uname VARCHAR(10) NOT NULL,      
    Uemail VARCHAR(50) UNIQUE NOT NULL, 
    Upwd VARCHAR(20) NOT NULL,        
    Join_date DATE   
);

CREATE TABLE ARTIST (
    Artist_idx INT AUTO_INCREMENT PRIMARY KEY,
    Artist_name VARCHAR(50) NOT NULL,              
    Info TEXT                               
);

CREATE TABLE ALBUM (
    Album_idx INT AUTO_INCREMENT PRIMARY KEY, 
    Album_name VARCHAR(100) NOT NULL,         
    Description TEXT,                        
    Release_date DATE,                        
    Admin_idx INT NOT NULL,                  
    Owner_artist_idx INT NOT NULL,                           
    FOREIGN KEY (Admin_idx) REFERENCES ADMIN(Aidx) ON DELETE CASCADE, 
    FOREIGN KEY (Owner_artist_idx) REFERENCES ARTIST(Artist_idx) ON DELETE CASCADE
);

CREATE TABLE MUSIC (
    Music_idx INT AUTO_INCREMENT PRIMARY KEY, 
    Music_name VARCHAR(100) NOT NULL,             
    Duration TIME,                           
    Lyrics TEXT,                             
    Genre VARCHAR(20),                      
    Likes_cnt INT DEFAULT 0,               
    Streaming_cnt INT DEFAULT 0,            
	Inc_Album_idx INT NOT NULL,
    FOREIGN KEY (Inc_Album_idx) REFERENCES ALBUM(Album_idx) ON DELETE CASCADE
);

CREATE TABLE PLAYLIST (
    Playlist_idx INT AUTO_INCREMENT PRIMARY KEY,
    Playlist_name VARCHAR(100) NOT NULL,
    Owner_user_idx INT,
    FOREIGN KEY (Owner_user_idx) REFERENCES USER(Uidx) ON DELETE CASCADE 
);

CREATE TABLE PLAYLIST_MUSIC (
    Play_idx INT NOT NULL,
    Music_idx INT NOT NULL,  
    PRIMARY KEY (Play_idx, Music_idx),
    FOREIGN KEY (Play_idx) REFERENCES PLAYLIST(Playlist_idx) ON DELETE CASCADE,
    FOREIGN KEY (Music_idx) REFERENCES MUSIC(Music_idx) ON DELETE CASCADE 
);

CREATE TABLE SINGERS (
	Music_idx INT NOT NULL,
    Singer_idx INT NOT NULL,
    PRIMARY KEY (Music_idx, Singer_idx),
    FOREIGN KEY (Music_idx) REFERENCES MUSIC(Music_idx) ON DELETE CASCADE, 
    FOREIGN KEY (Singer_idx) REFERENCES ARTIST(Artist_idx) ON DELETE CASCADE
);
CREATE TABLE TITLESONG (
    Album_idx INT NOT NULL,   
    Music_idx INT NOT NULL,   
    PRIMARY KEY (Album_idx, Music_idx), 
    FOREIGN KEY (Album_idx) REFERENCES ALBUM(Album_idx) ON DELETE CASCADE,
    FOREIGN KEY (Music_idx) REFERENCES MUSIC(Music_idx) ON DELETE CASCADE 
);

CREATE TABLE LYRICIST (
    Music_idx INT NOT NULL,
    Lyricist_name VARCHAR(100),
    PRIMARY KEY (Music_idx, Lyricist_name),
    FOREIGN KEY (Music_idx) REFERENCES MUSIC(Music_idx) ON DELETE CASCADE
);

CREATE TABLE COMPOSER (
    Music_idx INT NOT NULL,     
    Composer_name VARCHAR(100), 
    PRIMARY KEY (Music_idx, Composer_name),
    FOREIGN KEY (Music_idx) REFERENCES MUSIC(Music_idx) ON DELETE CASCADE
);

CREATE TABLE LIKE_ARTIST (
    User_idx INT NOT NULL, 
    Artist_idx INT NOT NULL,
    PRIMARY KEY (User_idx, Artist_idx),
    FOREIGN KEY (User_idx) REFERENCES USER(Uidx) ON DELETE CASCADE,
    FOREIGN KEY (Artist_idx) REFERENCES ARTIST(Artist_idx) ON DELETE CASCADE
);

CREATE TABLE LIKE_MUSIC (
	User_idx INT NOT NULL,
    Music_idx INT NOT NULL,
    PRIMARY KEY (User_idx, Music_idx),
    FOREIGN KEY (User_idx) REFERENCES USER(Uidx) ON DELETE CASCADE,
    FOREIGN KEY (Music_idx) REFERENCES MUSIC(Music_idx) ON DELETE CASCADE
);