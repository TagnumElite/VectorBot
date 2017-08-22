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
-- Now we create a user that can be access from any ip address by the password: 'PASSWORD'
-- It is recommended you change the password to something more secure!
CREATE USER IF NOT EXISTS 'Vector'@'%' IDENTIFIED BY 'PASSWORD';
-- Give that users those privileges to to do what ever it wants on the database
-- we created earlier
GRANT ALL privileges on vectorbot.* to Vector;
-- Flush Privileges
FLUSH PRIVILEGES;
/*
Now we create the ServerDB
*/
CREATE TABLE `vectorbot`.`vb_servers` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `server_id` VARCHAR(100) NOT NULL COMMENT 'The ID of the server. Stored as an string',
  `owner_id` VARCHAR(100) NOT NULL COMMENT 'The ID of the owner. Stored as a string.',
  `created_at` DATETIME NOT NULL COMMENT 'The datetime creation of the server. Stored as DATETIME',
  PRIMARY KEY (`id`),
  UNIQUE INDEX `server_id_UNIQUE` (`server_id` ASC))
COMMENT = 'This is where we will be storing the server unchanging data.';

CREATE TABLE `vectorbot`.`vb_servers_meta` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `server_id` VARCHAR(100) NOT NULL COMMENT 'The ID of the server. Stored as an string',
  `key` VARCHAR(100) NOT NULL COMMENT 'The Name of the content being stored!',
  `value` VARCHAR(10000) NOT NULL COMMENT 'The Content being stored',
  PRIMARY KEY (`id`))
COMMENT = 'This is where we will be storing the servers changeable data.';

/*
Now we create the MessageDB
*/
CREATE TABLE `vectorbot`.`vb_messages` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `message_id` VARCHAR(100) NOT NULL COMMENT 'The ID of the message. Stored as an string',
  `server_id` VARCHAR(100) NOT NULL COMMENT 'The ID of the message\'s server. Stored as an string',
  `channel_id` VARCHAR(100) NOT NULL COMMENT 'The ID of the message\'s channel. Stored as an string',
  `author_id` VARCHAR(100) NOT NULL COMMENT 'The ID of the message\'s author. Stored as an string',
  `created_at` DATETIME NOT NULL COMMENT 'The datetime creation of the message. Stored as DATETIME',
  PRIMARY KEY (`id`),
  UNIQUE INDEX `message_id_UNIQUE` (`message_id` ASC))
COMMENT = 'This is where we will be storing the messages main unchanging data.';

CREATE TABLE `vectorbot`.`vb_messages_meta` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `message_id` VARCHAR(100) NOT NULL COMMENT 'The ID of the message. Stored as an string',
  `key` VARCHAR(100) NOT NULL COMMENT 'The Name of the content being stored!',
  `value` VARCHAR(10000) NOT NULL COMMENT 'The Content being stored',
  PRIMARY KEY (`id`))
COMMENT = 'This is where we will be storing the messages changeable data.';

/*
Now we create the UserDB
I have no support for the UserDB
*/
CREATE TABLE `vectorbot`.`vb_users` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `user_id` VARCHAR(100) NOT NULL COMMENT 'The ID of the user. Stored as an string',
  `created_at` DATETIME NOT NULL COMMENT 'The datetime creation of the u. Stored as DATETIME',
  PRIMARY KEY (`id`),
  UNIQUE INDEX `user_id_UNIQUE` (`user_id` ASC))
COMMENT = 'This is where we will be storing the users unchanging data.';

CREATE TABLE `vectorbot`.`vb_users_meta` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `user_id` VARCHAR(100) NOT NULL COMMENT 'The ID of the user. Stored as an string',
  `key` VARCHAR(100) NOT NULL COMMENT 'The Name of the content being stored!',
  `value` VARCHAR(10000) NOT NULL COMMENT 'The Content being stored',
  PRIMARY KEY (`id`))
COMMENT = 'This is where we will be storing the user\'s changeable data.';
