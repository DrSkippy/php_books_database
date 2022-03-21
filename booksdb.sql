--
-- Table structure for table `book collection`
--

DROP TABLE IF EXISTS `book collection`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `book collection` (
  `BookCollectionID` int(11) NOT NULL auto_increment,
  `Title` varchar(200) NOT NULL,
  `Author` varchar(200) NOT NULL,
  `CopyrightDate` datetime default NULL,
  `ISBNNumber` varchar(13) default NULL,
  `PublisherName` varchar(50) default NULL,
  `CoverType` varchar(30) default NULL,
  `Pages` smallint(6) default NULL,
-- 2022-03-21 `LastRead` datetime NOT NULL default '0000-00-00 00:00:00',
-- 2022-03-21  `PreviouslyRead` datetime NOT NULL default '0000-00-00 00:00:00',
  `Category` varchar(10) default NULL,
  `Note` mediumtext,
  `Recycled` tinyint(1) default NULL,
  `Location` varchar(50) NOT NULL,
  `ISBNNumber13` varchar(13) default NULL,
  PRIMARY KEY  (`BookCollectionID`),
  KEY `LastRead_idx` (`LastRead`),
  KEY `Location_idx` (`Location`),
  FULLTEXT KEY `Author_idx` (`Author`),
  FULLTEXT KEY `Title_idx` (`Title`)
) ENGINE=MyISAM AUTO_INCREMENT=7000 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tags`
--

DROP TABLE IF EXISTS `tags`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tags` (
  `BookID` varchar(50) default NULL,
  `TagID` int(11) NOT NULL auto_increment,
  `Tag` varchar(50) default NULL,
  PRIMARY KEY  (`TagID`),
  KEY `BookID_idx` (`BookID`),
  FULLTEXT KEY `Tag_idx` (`Tag`)
) ENGINE=MyISAM AUTO_INCREMENT=7000 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

-- Dump completed on 2013-11-30 15:00:20

--
-- Table structure for table `books read`
--

DROP TABLE IF EXISTS `books read`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `books read` (
 `BookCollectionID` int(10) unsigned NOT NULL,
 `ReadDate` date NOT NULL,
 `ReadNote` text CHARACTER SET utf8,
 PRIMARY KEY (`BookCollectionID`,`ReadDate`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;