INSERT INTO schema_version (major, middle, minor) VALUES (1, 2, 0);

ALTER TABLE  `team` CHANGE  `name`  `name` VARCHAR( 128 ) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL ,
CHANGE  `color`  `color` VARCHAR( 32 ) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL;

CREATE TABLE  `skills_report` (
`id` INT( 11 ) NOT NULL AUTO_INCREMENT PRIMARY KEY ,
`submitted_by_id` INT( 11 ) NOT NULL ,
`updated` TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL
) ENGINE = INNODB;

ALTER TABLE  `skills` ADD  `skills_report_id` INT( 11 ) NULL DEFAULT NULL AFTER  `id` ,
ADD INDEX (  `skills_report_id` );

ALTER TABLE  `skills_report` ADD  `team_id` INT( 11 ) NOT NULL AFTER  `submitted_by_id` ,
ADD INDEX (  `team_id` );

ALTER TABLE  `skills_report` ADD INDEX (  `submitted_by_id` );

ALTER TABLE  `skills_report` ADD FOREIGN KEY (  `submitted_by_id` ) REFERENCES  `auth_user` (
`id`
) ON DELETE NO ACTION ON UPDATE CASCADE ;

ALTER TABLE  `skills_report` ADD FOREIGN KEY (  `team_id` ) REFERENCES  `team` (
`id`
) ON DELETE NO ACTION ON UPDATE CASCADE ;

ALTER TABLE  `skills` ADD FOREIGN KEY (  `skills_report_id` ) REFERENCES  `skills_report` (
`id`
) ON DELETE NO ACTION ON UPDATE CASCADE ;

ALTER TABLE  `skills` CHANGE  `athletic`  `athletic` INT( 11 ) NOT NULL DEFAULT  '0',
CHANGE  `experience`  `experience` INT( 11 ) NOT NULL DEFAULT  '0',
CHANGE  `forehand`  `forehand` INT( 11 ) NOT NULL DEFAULT  '0',
CHANGE  `backhand`  `backhand` INT( 11 ) NOT NULL DEFAULT  '0',
CHANGE  `receive`  `receive` INT( 11 ) NOT NULL DEFAULT  '0',
CHANGE  `strategy`  `strategy` INT( 11 ) NOT NULL DEFAULT  '0',
CHANGE  `position`  `position` INT( 11 ) NOT NULL DEFAULT  '0',
CHANGE  `spirit`  `spirit` INT( 11 ) NOT NULL DEFAULT  '7';

ALTER TABLE  `league` CHANGE  `night`  `night` VARCHAR( 32 ) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL ,
CHANGE  `season`  `season` VARCHAR( 32 ) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL ,
CHANGE  `gender`  `gender` VARCHAR( 32 ) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL ,
CHANGE  `gender_note`  `gender_note` TEXT CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL ,
CHANGE  `times`  `times` TEXT CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL ,
CHANGE  `mail_check_address`  `mail_check_address` TEXT CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL ,
CHANGE  `league_email`  `league_email` VARCHAR( 64 ) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL ,
CHANGE  `league_captains_email`  `league_captains_email` VARCHAR( 64 ) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL ,
CHANGE  `division_email`  `division_email` VARCHAR( 64 ) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL;

CREATE TABLE  `game_report` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `team_id` int(11) NOT NULL,
  `game_id` int(11) NOT NULL,
  `last_updated_by_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `team_id` (`team_id`),
  KEY `game_id` (`game_id`),
  KEY `last_updated_by_id` (`last_updated_by_id`)
) ENGINE = INNODB CHARACTER SET utf8 COLLATE utf8_general_ci;

CREATE TABLE  `game_report_attendance` (
  `id` INT( 11 ) NOT NULL AUTO_INCREMENT,
  `report_id` INT( 11 ) NOT NULL ,
  `user_id` INT( 11 ) NOT NULL ,
  `last_updated` TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (  `id` ),
  KEY `report_id` (`report_id`),
  KEY `user_id` (`user_id`)
) ENGINE = INNODB CHARACTER SET utf8 COLLATE utf8_general_ci;

CREATE TABLE  `game_report_comment` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `report_id` int(11) NOT NULL,
  `submitted_by_id` int(11) NOT NULL,
  `comment` text NOT NULL,
  PRIMARY KEY (`id`),
  KEY `report_id` (`report_id`),
  KEY `submitted_by_id` (`submitted_by_id`)
) ENGINE = INNODB CHARACTER SET utf8 COLLATE utf8_general_ci;

CREATE TABLE  `game_report_scores` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `report_id` int(11) NOT NULL,
  `team_id` int(11) NOT NULL,
  `score` int(3) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `report_id` (`report_id`),
  KEY `team_id` (`team_id`)
) ENGINE = INNODB CHARACTER SET utf8 COLLATE utf8_general_ci;

ALTER TABLE `game_report`
  ADD CONSTRAINT `game_report_ibfk_3` FOREIGN KEY (`last_updated_by_id`) REFERENCES `auth_user` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `game_report_ibfk_1` FOREIGN KEY (`team_id`) REFERENCES `team` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `game_report_ibfk_2` FOREIGN KEY (`game_id`) REFERENCES `game` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE  `game_report_attendance` ADD FOREIGN KEY (  `report_id` ) REFERENCES  `game_report` (
`id`
) ON DELETE CASCADE ON UPDATE CASCADE ;

ALTER TABLE  `game_report_attendance` ADD FOREIGN KEY (  `user_id` ) REFERENCES  `auth_user` (
`id`
) ON DELETE CASCADE ON UPDATE CASCADE ;

ALTER TABLE `game_report_comment`
  ADD CONSTRAINT `game_report_comment_ibfk_1` FOREIGN KEY (`report_id`) REFERENCES `game_report` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `game_report_comment_ibfk_2` FOREIGN KEY (`submitted_by_id`) REFERENCES `auth_user` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `game_report_scores`
  ADD CONSTRAINT `game_report_scores_ibfk_1` FOREIGN KEY (`report_id`) REFERENCES `game_report` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `game_report_scores_ibfk_2` FOREIGN KEY (`team_id`) REFERENCES `team` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE  `game_report_comment` ADD  `spirit` INT( 3 ) NOT NULL AFTER  `submitted_by_id`;