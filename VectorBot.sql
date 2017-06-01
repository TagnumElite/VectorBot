/*
WELCOME MY DEAR ONLOOKER
My SQL knowledge is horrible so therefor the commands inside this file
may look atrosious as well as my spelling. (I am lazy just to let you know)

For now what this is supposed to do is pre-create the tables for you, the reason I
don't pre-create the dev tables anymore is because I like to make sure they work,
that's why every time you run this script the dev tables get deleted

In the future I want to move to something like wordpresses meta system so that I don't
have to DROP, CREATE and ALTER tables anymore.
*/

-- We create the Schema/Database to use only if it doesn't exists
CREATE SCHEMA IF NOT EXISTS vectorbot;
-- Select that table we just created
SELECT vectorbot;
-- Now we create a user that can be access from any ip address by the password: 'PASSWORD'
-- It is recommended you change the password to something more secure!
CREATE USER IF NOT EXISTS 'Vector'@'%' IDENTIFIED BY 'PASSWORD';
-- Give that users those privileges to to do what ever it wants on the database
-- we created earlier
GRANT ALL privileges on vectorbot.* to Vector;
-- Drop the dev tables, if you want to keep those tables just add an '-- ' to the start
-- of the line. Example: '-- DROP TABLE IF EXISTS vd_servers, vd_messages, vd_members;'
DROP TABLE IF EXISTS vd_servers, vd_messages, vd_members;

/*
Now we create the ServerDB
*/
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

CREATE TABLE `vectorbot`.`vb_members` (
  `id` INT NOT NULL,
  `username` VARCHAR(45) NOT NULL,
  `discriminator` INT NOT NULL,
  `avatar_url` VARCHAR(45) NULL,
  `default_url` VARCHAR(45) NOT NULL,
  `status` VARCHAR(45) NULL,
  `game` VARCHAR(45) NULL,
  `servers` JSON NULL,
  `confs` JSON NULL,
  `created_at` DATETIME NOT NULL,
  PRIMARY KEY (`id`))
COMMENT = 'Here is where the members are stored!';


/*
After we create the Tables we must create the functions

sadly i have no functions right now :(
*/
