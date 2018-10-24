/*
Navicat MySQL Data Transfer

Source Server         : vagrant
Source Server Version : 50639
Source Host           : localhost:3306
Source Database       : scrapy

Target Server Type    : MYSQL
Target Server Version : 50639
File Encoding         : 65001

Date: 2018-10-24 17:59:45
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for bqg_book
-- ----------------------------
DROP TABLE IF EXISTS `bqg_book`;
CREATE TABLE `bqg_book` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `unique_code` char(32) NOT NULL,
  `title` varchar(128) DEFAULT NULL,
  `author` varchar(128) DEFAULT NULL,
  `last_update` date DEFAULT NULL,
  `description` text,
  `image_local_url` varchar(128) DEFAULT NULL,
  `image_origin_url` varchar(128) DEFAULT NULL,
  `url` varchar(128) DEFAULT NULL,
  `finished` tinyint(2) DEFAULT '0',
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=752 DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for bqg_chapter
-- ----------------------------
DROP TABLE IF EXISTS `bqg_chapter`;
CREATE TABLE `bqg_chapter` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `book_unique_code` char(32) DEFAULT NULL,
  `unique_code` char(32) DEFAULT NULL,
  `prev_unique_code` char(32) DEFAULT NULL,
  `next_unique_code` char(32) DEFAULT NULL,
  `title` varchar(128) DEFAULT NULL,
  `content` text,
  `view` int(11) unsigned DEFAULT NULL,
  `url` varchar(128) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
