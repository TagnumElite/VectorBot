# This is just incase if you want to speed things up!
CREATE SCHEMA IF NOT EXISTS vectorbot;
CREATE USER IF NOT EXISTS 'Vector'@'%' IDENTIFIED BY 'PASSWORD';
GRANT ALL privileges on vectorbot.* to Vector;

# Create Server Tables
CREATE TABLE IF NOT EXISTS `vectorbot`.`vb_servers` (
  `id` BIGINT(18) NOT NULL,
  `name` VARCHAR(45) NOT NULL,
  `members` JSON NOT NULL,
  `default_role` VARCHAR(45) NOT NULL,
  `default_channel` VARCHAR(45) NOT NULL,
  `roles` JSON NOT NULL,
  `channels` JSON NOT NULL,
  `config` JSON,
  `emojis` JSON NULL,
  `afk_timeout` INT NULL,
  `region` ENUM('Brazil', 'Central Europe', 'Hong Kong', 'Russia', 'Singapore', 'Sydney', 'US Central', 'US East', 'US South', 'US West', 'Western Europe') NOT NULL,
  `afk_channel` VARCHAR(45) NULL,
  `icon_url` TEXT(30) NULL,
  `owner` VARCHAR(45) NOT NULL,
  `status` TINYINT NOT NULL DEFAULT 1,
  `large` TINYINT NOT NULL DEFAULT 0,
  `mfa` TINYINT NOT NULL DEFAULT 0,
  `verfication_level` ENUM('None', 'Low', 'Medium', 'High', 'Table Flip') NOT NULL DEFAULT 'None',
  `splash` VARCHAR(45) NULL,
  `size` REAL NOT NULL DEFAULT 1,
  `created` DATETIME NOT NULL,
  PRIMARY KEY (`id`));

CREATE TABLE IF NOT EXISTS `vectorbot`.`vb_messages` (
  `id` BIGINT(18) NOT NULL,
  `server_id` VARCHAR(45) NOT NULL,
  `channel_id` VARCHAR(45) NOT NULL,
  `author_id` VARCHAR(45) NOT NULL,
  `content` JSON NOT NULL,
  `mention_everyone` TINYINT NULL DEFAULT 0,
  `mentions` JSON NULL,
  `channel_mentions` JSON NULL,
  `role_mentions` JSON NULL,
  `attachments` LONGTEXT NULL,
  `pinned` TINYINT NULL DEFAULT 0,
  `reactions` JSON NULL,
  PRIMARY KEY (`id`));

CREATE TABLE IF NOT EXISTS `vectorbot`.`vb_users` (
  `id` BIGINT(18) NOT NULL,
  `username` VARCHAR(45) NOT NULL,
  `discriminator` VARCHAR(45) NOT NULL,
  `avatar_url` VARCHAR(45) NULL,
  `default_url` VARCHAR(45) NOT NULL,
  `servers` JSON NULL,
  `status` ENUM('online', 'idle', 'dnd', 'offline') NOT NULL DEFAULT 'offline',
  `game` LONGTEXT NULL,
  PRIMARY KEY (`id`));

# Create Dev Server Tables
CREATE TABLE IF NOT EXISTS `vectorbot`.`vd_servers` (
  `id` BIGINT(18) NOT NULL,
  `name` VARCHAR(45) NOT NULL,
  `members` JSON NOT NULL,
  `default_role` VARCHAR(45) NOT NULL,
  `default_channel` VARCHAR(45) NOT NULL,
  `roles` JSON NOT NULL,
  `channels` JSON NOT NULL,
  `config` JSON,
  `emojis` JSON NULL,
  `afk_timeout` INT NULL,
  `region` ENUM('Brazil', 'Central Europe', 'Hong Kong', 'Russia', 'Singapore', 'Sydney', 'US Central', 'US East', 'US South', 'US West', 'Western Europe') NOT NULL,
  `afk_channel` VARCHAR(45) NULL,
  `icon_url` TEXT(30) NULL,
  `owner` VARCHAR(45) NOT NULL,
  `offline` TINYINT NOT NULL DEFAULT 1,
  `large` TINYINT NOT NULL DEFAULT 0,
  `mfa` TINYINT NOT NULL DEFAULT 0,
  `verfication_level` ENUM('None', 'Low', 'Medium', 'High', 'Table Flip') NOT NULL DEFAULT 'None',
  `splash` VARCHAR(45) NULL,
  `size` REAL NOT NULL DEFAULT 1,
  `created` DATETIME NOT NULL,
  PRIMARY KEY (`id`));

CREATE TABLE IF NOT EXISTS `vectorbot`.`vd_messages` (
  `id` BIGINT(18) NOT NULL,
  `server_id` VARCHAR(45) NOT NULL,
  `channel_id` VARCHAR(45) NOT NULL,
  `author_id` VARCHAR(45) NOT NULL,
  `content` JSON NOT NULL,
  `mention_everyone` TINYINT NULL DEFAULT 0,
  `mentions` JSON NULL,
  `channel_mentions` JSON NULL,
  `role_mentions` JSON NULL,
  `attachments` LONGTEXT NULL,
  `pinned` TINYINT NULL DEFAULT 0,
  `reactions` JSON NULL,
  PRIMARY KEY (`id`));

CREATE TABLE IF NOT EXISTS `vectorbot`.`vd_users` (
  `id` BIGINT(18) NOT NULL,
  `username` VARCHAR(45) NOT NULL,
  `discriminator` VARCHAR(45) NOT NULL,
  `avatar_url` VARCHAR(45) NULL,
  `default_url` VARCHAR(45) NOT NULL,
  `servers` JSON NULL,
  `status` ENUM('online', 'idle', 'dnd', 'offline') NOT NULL DEFAULT 'offline',
  `game` LONGTEXT NULL,
  PRIMARY KEY (`id`));
