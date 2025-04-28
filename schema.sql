CREATE TABLE anime (
    name VARCHAR(255) PRIMARY KEY,
    reviewScore INT,
    ageRating INT, 
    airedDate DATETIME NOT NULL,  
    episodes INT NOT NULL DEFAULT 0,  
    duration INT,
    summary VARCHAR(1000), 
    type ENUM('tv', 'movies'),  
    sourceType ENUM('manga', 'lightNovel'), 
    languageType ENUM('sub', 'dub'),
    directed VARCHAR(255),
    imageURL VARCHAR(1000),
    FOREIGN KEY (directed) REFERENCES studios(name)
);

CREATE TABLE animeHasGenre (
    id INT AUTO_INCREMENT PRIMARY KEY,
    animeName VARCHAR(255),
    genreName VARCHAR(255),
    FOREIGN KEY (animeName) REFERENCES anime(name),
    FOREIGN KEY (genreName) REFERENCES genre(genreName)
);

CREATE TABLE animeHasPlatform (
    id INT AUTO_INCREMENT PRIMARY KEY,
    animeName VARCHAR(255),
    platformName VARCHAR(255),
    FOREIGN KEY (animeName) REFERENCES anime(name),
    FOREIGN KEY (platformName) REFERENCES streamingPlatform(name)
);

CREATE TABLE animeList (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    type ENUM('recommendedToUser', 'watchList', 'previouslyWatched')
);

CREATE TABLE animeListItem (
    id INT AUTO_INCREMENT PRIMARY KEY,
    listIndex INT NOT NULL,
    listID INT,
    animeName VARCHAR(255),
    FOREIGN KEY (listID) REFERENCES animeList(id),
    FOREIGN KEY (animeName) REFERENCES anime(name)
);

CREATE TABLE genre (
    genreName VARCHAR(255) PRIMARY KEY
);

CREATE TABLE streamingPlatform (
    name VARCHAR(255) PRIMARY KEY,
    platformURL VARCHAR(2083) NOT NULL
);

CREATE TABLE studios (
    name VARCHAR(255) PRIMARY KEY,
    specializationType ENUM('tv', 'movies')
);

CREATE TABLE user (
    username VARCHAR(255) NOT NULL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    recommendedToUser INT,
    watchList INT,
    previouslyWatched INT,
    FOREIGN KEY (recommendedToUser) REFERENCES animeList(id),
    FOREIGN KEY (watchList) REFERENCES animeList(id),
    FOREIGN KEY (previouslyWatched) REFERENCES animeList(id)
);
