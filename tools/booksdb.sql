--
-- Table structure for table `book collection`
--
-- scott.`book collection` definition

DROP TABLE IF EXISTS `book collection`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `book collection` (
  `BookCollectionID` int(11) NOT NULL AUTO_INCREMENT,
  `Title` varchar(200) NOT NULL,
  `Author` varchar(200) NOT NULL,
  `CopyrightDate` datetime DEFAULT NULL,
  `ISBNNumber` varchar(13) DEFAULT NULL,
  `PublisherName` varchar(50) DEFAULT NULL,
  `CoverType` varchar(30) DEFAULT NULL,
  `Pages` smallint(6) DEFAULT NULL,
  `Category` varchar(10) DEFAULT NULL,
  `Note` mediumtext,
  `Recycled` tinyint(1) DEFAULT NULL,
  `Location` varchar(50) NOT NULL,
  `ISBNNumber13` varchar(13) DEFAULT NULL,
  PRIMARY KEY (`BookCollectionID`),
  KEY `Location_idx` (`Location`),
  FULLTEXT KEY `Author_idx` (`Author`),
  FULLTEXT KEY `Title_idx` (`Title`)
) ENGINE=MyISAM AUTO_INCREMENT=1743 DEFAULT CHARSET=utf8


--
-- Table structure for table `books read`
--
DROP TABLE IF EXISTS `books read`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
-- scott.`books read` definition

CREATE TABLE `books read` (
  `BookCollectionID` int(10) unsigned NOT NULL,
  `ReadDate` date NOT NULL,
  `ReadNote` text CHARACTER SET utf8,
  PRIMARY KEY (`BookCollectionID`,`ReadDate`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `books read`
--
DROP TABLE IF EXISTS `tag labels`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
-- scott.`tag labels` definition
CREATE TABLE `tag labels` (
  `TagID` int(11) NOT NULL AUTO_INCREMENT,
  `Label` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`TagID`)
) ENGINE=MyISAM AUTO_INCREMENT=1085 DEFAULT CHARSET=utf8
/*!40101 SET character_set_client = @saved_cs_client */;


--
-- Table structure for table `books tags`
--
DROP TABLE IF EXISTS `books tags`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
-- scott.`books tags` definition
CREATE TABLE `books tags` (
  `BookID` varchar(50) NOT NULL,
  `Tag_ID` int(11) NOT NULL,
  PRIMARY KEY (`BookID`,`Tag_ID`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8
/*!40101 SET character_set_client = @saved_cs_client */;


--
-- DEPRECATED -- DEPRECATED -- DEPRECATED -- DEPRECATED --
-- Table structure for table `tags`
--
DROP TABLE IF EXISTS `tags`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
-- scott.tags definition

CREATE TABLE `tags` (
  `BookID` varchar(50) NOT NULL DEFAULT '',
  `TagID` int(11) NOT NULL AUTO_INCREMENT,
  `Tag` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`BookID`,`TagID`),
  KEY `BookID_idx` (`BookID`),
  FULLTEXT KEY `Tag_idx` (`Tag`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;