-- books.`book collection` definition

CREATE TABLE `book collection` (
  `BookCollectionID` int NOT NULL AUTO_INCREMENT,
  `Title` varchar(200) NOT NULL,
  `Author` varchar(200) NOT NULL,
  `CopyrightDate` datetime DEFAULT NULL,
  `ISBNNumber` varchar(13) DEFAULT NULL,
  `PublisherName` varchar(50) DEFAULT NULL,
  `CoverType` varchar(30) DEFAULT NULL,
  `Pages` smallint DEFAULT NULL,
  `Category` varchar(10) DEFAULT NULL,
  `Note` mediumtext,
  `Recycled` tinyint(1) DEFAULT NULL,
  `Location` varchar(50) NOT NULL,
  `ISBNNumber13` varchar(13) DEFAULT NULL,
  `LastUpdate` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`BookCollectionID`),
  KEY `Location_idx` (`Location`),
  FULLTEXT KEY `Author_idx` (`Author`),
  FULLTEXT KEY `Title_idx` (`Title`)
) ENGINE=MyISAM AUTO_INCREMENT=1807 DEFAULT CHARSET=utf8mb3;


-- books.`books read` definition

CREATE TABLE `books read` (
  `BookCollectionID` int unsigned NOT NULL,
  `ReadDate` date NOT NULL,
  `ReadNote` text CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci,
  `LastUpdate` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`BookCollectionID`,`ReadDate`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;


-- books.`books tags` definition

CREATE TABLE `books tags` (
  `BookID` varchar(50) NOT NULL,
  `TagID` int NOT NULL,
  `LastUpdate` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`BookID`,`TagID`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb3;


-- books.`complete date estimates` definition

CREATE TABLE `complete date estimates` (
  `BookCollectionID` bigint unsigned NOT NULL,
  `StartDate` datetime NOT NULL,
  `LastReadablePage` bigint NOT NULL,
  `EstimateDate` datetime DEFAULT NULL,
  `EstimatedFinishDate` datetime DEFAULT NULL,
  `RecordID` bigint unsigned NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`RecordID`)
) ENGINE=InnoDB AUTO_INCREMENT=30 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


-- books.`daily page records` definition

CREATE TABLE `daily page records` (
  `RecordDate` datetime NOT NULL,
  `page` bigint NOT NULL,
  `RecordID` bigint unsigned NOT NULL,
  `LastUpdate` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`RecordID`,`RecordDate`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


-- books.`tag labels` definition

CREATE TABLE `tag labels` (
  `TagID` int NOT NULL AUTO_INCREMENT,
  `Label` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`TagID`),
  UNIQUE KEY `tag_labels_UN` (`Label`)
) ENGINE=MyISAM AUTO_INCREMENT=1211 DEFAULT CHARSET=utf8mb3;


