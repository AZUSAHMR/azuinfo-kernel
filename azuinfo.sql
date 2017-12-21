-- MySQL dump 10.14  Distrib 5.5.57-MariaDB, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: azuinfo
-- ------------------------------------------------------
-- Server version	5.5.57-MariaDB-1ubuntu0.14.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `azuinfo_popn_song`
--

DROP TABLE IF EXISTS `azuinfo_popn_song`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `azuinfo_popn_song` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `uniq` varchar(40) NOT NULL,
  `title` varchar(100) NOT NULL,
  `genre` varchar(100) NOT NULL,
  `artist` varchar(100) DEFAULT NULL,
  `easy` int(11) DEFAULT NULL,
  `normal` int(11) DEFAULT NULL,
  `hyper` int(11) DEFAULT NULL,
  `ex` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uniq` (`uniq`)
) ENGINE=InnoDB AUTO_INCREMENT=1309 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `azuinfo_sdvx_song`
--

DROP TABLE IF EXISTS `azuinfo_sdvx_song`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `azuinfo_sdvx_song` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `uniq` varchar(40) NOT NULL,
  `title` varchar(100) NOT NULL,
  `artist` varchar(100) NOT NULL,
  `effector_nov` varchar(100) DEFAULT NULL,
  `effector_adv` varchar(100) DEFAULT NULL,
  `effector_exh` varchar(100) DEFAULT NULL,
  `effector_mxm` varchar(100) DEFAULT NULL,
  `effector_inf` varchar(100) DEFAULT NULL,
  `illustrator_nov` varchar(100) DEFAULT NULL,
  `illustrator_adv` varchar(100) DEFAULT NULL,
  `illustrator_exh` varchar(100) DEFAULT NULL,
  `illustrator_mxm` varchar(100) DEFAULT NULL,
  `illustrator_inf` varchar(100) DEFAULT NULL,
  `grv` int(11) DEFAULT NULL,
  `nov` int(11) DEFAULT NULL,
  `adv` int(11) DEFAULT NULL,
  `exh` int(11) DEFAULT NULL,
  `mxm` int(11) DEFAULT NULL,
  `inf` int(11) DEFAULT NULL,
  `albumart_nov` varchar(100) DEFAULT NULL,
  `albumart_adv` varchar(100) DEFAULT NULL,
  `albumart_exh` varchar(100) DEFAULT NULL,
  `albumart_mxm` varchar(100) DEFAULT NULL,
  `albumart_inf` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uniq` (`uniq`),
  UNIQUE KEY `albumart_nov` (`albumart_nov`),
  UNIQUE KEY `albumart_adv` (`albumart_adv`),
  UNIQUE KEY `albumart_exh` (`albumart_exh`),
  UNIQUE KEY `albumart_inf` (`albumart_inf`)
) ENGINE=InnoDB AUTO_INCREMENT=1027 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `azuinfo_user`
--

DROP TABLE IF EXISTS `azuinfo_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `azuinfo_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `konamiId` varchar(32) NOT NULL,
  `nickname` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `konamiId` (`konamiId`),
  UNIQUE KEY `nickname` (`nickname`)
) ENGINE=InnoDB AUTO_INCREMENT=4937 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `azuinfo_waiting`
--

DROP TABLE IF EXISTS `azuinfo_waiting`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `azuinfo_waiting` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `owner` int(11) NOT NULL,
  `device` int(11) NOT NULL,
  `status` int(11) NOT NULL,
  `swap` int(11) NOT NULL,
  `error` int(11) DEFAULT NULL,
  `request` int(11) NOT NULL,
  `start` int(11) DEFAULT NULL,
  `end` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=73748 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2017-12-22  0:00:08
