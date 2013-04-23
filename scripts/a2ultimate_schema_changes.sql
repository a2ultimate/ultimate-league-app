# Database Schema Changes


ALTER TABLE `attendance` ENGINE = INNODB DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci; ALTER TABLE `auth_group` ENGINE = INNODB DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci; ALTER TABLE `auth_group_permissions` ENGINE = INNODB DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci; ALTER TABLE `auth_message` ENGINE = INNODB DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci; ALTER TABLE `auth_permission` ENGINE = INNODB DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci; ALTER TABLE `auth_user` ENGINE = INNODB DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci; ALTER TABLE `auth_user_groups` ENGINE = INNODB DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci; ALTER TABLE `auth_user_user_permissions` ENGINE = INNODB DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci; ALTER TABLE `baggage` ENGINE = INNODB DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci; ALTER TABLE `django_admin_log` ENGINE = INNODB DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci; ALTER TABLE `django_content_type` ENGINE = INNODB DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci; ALTER TABLE `django_session` ENGINE = INNODB DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci; ALTER TABLE `django_site` ENGINE = INNODB DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci; ALTER TABLE `field` ENGINE = INNODB DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci; ALTER TABLE `field_league` ENGINE = INNODB DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci; ALTER TABLE `field_names` ENGINE = INNODB DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci; ALTER TABLE `game` ENGINE = INNODB DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci; ALTER TABLE `game_sponsor` ENGINE = INNODB DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci; ALTER TABLE `league` ENGINE = INNODB DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci; ALTER TABLE `league_skip_dates` ENGINE = INNODB DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci; ALTER TABLE `player` ENGINE = INNODB DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci; ALTER TABLE `player_info` ENGINE = INNODB DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci; ALTER TABLE `registration` ENGINE = INNODB DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci; ALTER TABLE `schedule` ENGINE = INNODB DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci; ALTER TABLE `score_report` ENGINE = INNODB DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci; ALTER TABLE `skills` ENGINE = INNODB DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci; ALTER TABLE `skills_type` ENGINE = INNODB DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci; ALTER TABLE `sponsor` ENGINE = INNODB DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci; ALTER TABLE `static_content` ENGINE = INNODB DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci; ALTER TABLE `static_nav_bar` ENGINE = INNODB DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci; ALTER TABLE `team` ENGINE = INNODB DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci; ALTER TABLE `team_member` ENGINE = INNODB DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;

DROP TABLE `test_car`, `test_manufacturer`, `player_info`;

TRUNCATE  `auth_user`;

ALTER TABLE `league` DROP `where_id`;

ALTER TABLE  `static_content` DROP INDEX  `static_content_nav_bar_id`;


/* ATTENDANCE */
ALTER TABLE  `attendance` ADD INDEX (  `player_id` );
# Player 179 and 499 have orphaned attendance records
DELETE FROM `attendance` WHERE `player_id` IN ( 179, 499 );
ALTER TABLE  `attendance` ADD FOREIGN KEY (  `player_id` ) REFERENCES  `player` (
`id`
) ON DELETE CASCADE ON UPDATE CASCADE ;

ALTER TABLE  `attendance` ADD INDEX (  `score_report_id` );
ALTER TABLE  `attendance` ADD FOREIGN KEY (  `score_report_id` ) REFERENCES  `score_report` (
`id`
) ON DELETE CASCADE ON UPDATE CASCADE ;

/* FIELD */
ALTER TABLE  `field` DROP  `league_id`;
UPDATE  `field` SET  `layout_link` =  'images/field_maps/wixom.jpg' WHERE  `field`.`id` =1;

UPDATE  `field` SET  `layout_link` =  'images/field_maps/fuller.png' WHERE  `field`.`id` =2;

UPDATE  `field` SET  `layout_link` =  'images/field_maps/scarlet.png' WHERE  `field`.`id` =4;

UPDATE  `field` SET  `layout_link` =  'images/field_maps/huron.jpg' WHERE  `field`.`id` =6;

UPDATE  `field` SET  `layout_link` =  'images/field_maps/olson.jpg' WHERE  `field`.`id` =11;


/* FIELD_LEAGUE */
ALTER TABLE `field_league` ADD `id` INT(5) UNSIGNED NOT NULL AUTO_INCREMENT FIRST, ADD PRIMARY KEY (`id`);
ALTER TABLE  `field_league` ADD INDEX (  `league_id` );
ALTER TABLE  `field_league` ADD FOREIGN KEY (  `league_id` ) REFERENCES  `league` (
`id`
) ON DELETE CASCADE ON UPDATE CASCADE ;

ALTER TABLE  `field_league` ADD INDEX (  `field_id` );
ALTER TABLE  `field_league` ADD FOREIGN KEY (  `field_id` ) REFERENCES  `field` (
`id`
) ON DELETE CASCADE ON UPDATE CASCADE ;


/* FIELD_NAMES */
ALTER TABLE  `field_names` ADD INDEX (  `field_id` );
ALTER TABLE  `field_names` ADD FOREIGN KEY (  `field_id` ) REFERENCES  `field` (
`id`
) ON DELETE CASCADE ON UPDATE CASCADE ;


/* GAME */
DELETE FROM `game` WHERE `game`.`id` = 195;
DELETE FROM `game` WHERE `game`.`id` = 196;

ALTER TABLE  `game` ADD INDEX (  `field_name_id` );
ALTER TABLE  `game` ADD FOREIGN KEY (  `field_name_id` ) REFERENCES  `field_names` (
`id`
) ON DELETE CASCADE ON UPDATE CASCADE ;

/* GAME_TEAM */
CREATE TABLE  `game_teams` (
`id` INT( 11 ) NOT NULL AUTO_INCREMENT PRIMARY KEY ,
`game_id` INT( 11 ) NOT NULL ,
`team_id` INT( 11 ) NOT NULL ,
INDEX (  `game_id` ,  `team_id` )
) ENGINE = INNODB;

ALTER TABLE  `game_teams` ADD FOREIGN KEY (  `game_id` ) REFERENCES  `game` (
`id`
) ON DELETE CASCADE ON UPDATE CASCADE ;

ALTER TABLE  `game_teams` ADD FOREIGN KEY (  `team_id` ) REFERENCES  `team` (
`id`
) ON DELETE CASCADE ON UPDATE CASCADE ;

INSERT INTO  `game_teams` (
SELECT  NULL AS `id`, `id` AS `game_id` ,  `team1_id` AS  `team_id`
FROM  `game` );

INSERT INTO  `game_teams` (
SELECT  NULL AS `id`, `id` AS `game_id` ,  `team2_id` AS  `team_id`
FROM  `game` );

ALTER TABLE  `game` DROP  `team1_id` ,
DROP  `team2_id` ;

/* GAME_SPONSOR */
DELETE FROM  `game_sponsor` WHERE  `game_sponsor`.`game_id` =195 AND  `game_sponsor`.`sponsor_id` =3;
DELETE FROM  `game_sponsor` WHERE  `game_sponsor`.`game_id` =196 AND  `game_sponsor`.`sponsor_id` =3;
ALTER TABLE  `game_sponsor` ADD INDEX (  `game_id` );
ALTER TABLE  `game_sponsor` ADD FOREIGN KEY (  `game_id` ) REFERENCES  `game` (
`id`
) ON DELETE CASCADE ON UPDATE CASCADE ;

ALTER TABLE  `game_sponsor` ADD INDEX (  `sponsor_id` );
ALTER TABLE  `game_sponsor` ADD FOREIGN KEY (  `sponsor_id` ) REFERENCES  `sponsor` (
`id`
) ON DELETE CASCADE ON UPDATE CASCADE ;


/* LEAGUE */
UPDATE  `league` SET  `night` =  'Spring Bonanza Hat Tournament' WHERE  `league`.`id` =49;


/* LEAGUE_SKIP_DATES */
ALTER TABLE  `league_skip_dates` ADD INDEX (  `league_id` );
ALTER TABLE  `league_skip_dates` ADD FOREIGN KEY (  `league_id` ) REFERENCES  `league` (
`id`
) ON DELETE CASCADE ON UPDATE CASCADE ;


/* REGISTRATION */
UPDATE `registration` SET `night` = 'Spring Bonanza Hat Tournament' WHERE `night` = 'spring bonanza';
ALTER TABLE `registration` ADD `league_id` INT(11) NOT NULL AFTER `id`;
UPDATE `registration` SET `league_id` = (SELECT `league`.`id` FROM `league` WHERE `league`.`night` = `registration`.`night` AND `league`.`season` = `registration`.`season` AND `league`.`year` = `registration`.`year`);
ALTER TABLE `registration` DROP `night`, DROP `season`, DROP `year`;
DELETE FROM `registration` WHERE `id` IN ( 4920, 4921, 4922, 4923, 4925 );
ALTER TABLE  `registration` ADD INDEX (  `league_id` );
-- ALTER TABLE  `registration` ADD FOREIGN KEY (  `league_id` ) REFERENCES  `league` (
-- `id`
-- ) ON DELETE CASCADE ON UPDATE CASCADE ;

ALTER TABLE  `registration` ADD INDEX (  `player_id` );
ALTER TABLE  `registration` ADD FOREIGN KEY (  `player_id` ) REFERENCES  `player` (
`id`
) ON DELETE CASCADE ON UPDATE CASCADE ;

ALTER TABLE  `registration` ADD INDEX (  `baggage_id` );
ALTER TABLE  `registration` ADD FOREIGN KEY (  `baggage_id` ) REFERENCES  `baggage` (
`id`
) ON DELETE CASCADE ON UPDATE CASCADE ;


/* SCHEDULE */
ALTER TABLE `schedule` ADD INDEX(`league_id`);
ALTER TABLE  `schedule` ADD FOREIGN KEY (  `league_id` ) REFERENCES  `league` (
`id`
) ON DELETE CASCADE ON UPDATE CASCADE ;


/* SCORE_REPORT */
ALTER TABLE `score_report` ADD INDEX(`reported_by_id`);
ALTER TABLE  `score_report` ADD FOREIGN KEY (  `reported_by_id` ) REFERENCES  `player` (
`id`
) ON DELETE CASCADE ON UPDATE CASCADE ;

ALTER TABLE  `score_report` ADD INDEX (  `game_id` );
# problem with game_id to games.id
# SELECT * FROM `score_report` LEFT JOIN game ON score_report.game_id = game.id WHERE schedule_id IS NULL
DELETE  `score_report` FROM  `score_report` LEFT JOIN game ON score_report.game_id = game.id WHERE schedule_id IS NULL;
ALTER TABLE  `score_report` ADD FOREIGN KEY (  `game_id` ) REFERENCES  `game` (
`id`
) ON DELETE CASCADE ON UPDATE CASCADE ;


/* SKILLS */
ALTER TABLE  `skills` ADD INDEX (  `skills_type_id` );
ALTER TABLE  `skills` ADD FOREIGN KEY (  `skills_type_id` ) REFERENCES  `skills_type` (
`id`
) ON DELETE CASCADE ON UPDATE CASCADE ;

ALTER TABLE  `skills` ADD INDEX (  `player_id` );
# problem with player_id to player.id
# SELECT * FROM `skills` LEFT JOIN player ON skills.player_id = player.id WHERE player.id IS NULL
DELETE `skills` FROM `skills` LEFT JOIN `player` ON skills.player_id = player.id WHERE player.id IS NULL;
ALTER TABLE  `skills` ADD FOREIGN KEY (  `player_id` ) REFERENCES  `player` (
`id`
) ON DELETE CASCADE ON UPDATE CASCADE ;

ALTER TABLE  `skills` ADD INDEX (  `submitted_by_id` );
# problem with submitted_by_id to player.id (fixed with above DELETE)
ALTER TABLE  `skills` ADD FOREIGN KEY (  `submitted_by_id` ) REFERENCES  `player` (
`id`
) ON DELETE CASCADE ON UPDATE CASCADE ;


/* TEAM */
ALTER TABLE  `team` ADD INDEX (  `league_id` );
ALTER TABLE  `team` ADD FOREIGN KEY (  `league_id` ) REFERENCES  `league` (
`id`
) ON DELETE CASCADE ON UPDATE CASCADE ;


/* TEAM_MEMBER */
ALTER TABLE  `team_member` ADD INDEX (  `team_id` );
# problem with team_id to team.id
# SELECT * FROM `team_member` LEFT JOIN team ON team_member.team_id = team.id WHERE team.id IS NULL
DELETE `team_member` FROM  `team_member` LEFT JOIN team ON team_member.team_id = team.id WHERE team.id IS NULL;
ALTER TABLE  `team_member` ADD FOREIGN KEY (  `team_id` ) REFERENCES  `team` (
`id`
) ON DELETE CASCADE ON UPDATE CASCADE ;

ALTER TABLE  `team_member` ADD INDEX (  `player_id` );
ALTER TABLE  `team_member` ADD FOREIGN KEY (  `player_id` ) REFERENCES  `player` (
`id`
) ON DELETE CASCADE ON UPDATE CASCADE ;




ALTER TABLE  `player` ADD  `salt` VARCHAR( 128 ) NOT NULL AFTER  `password` ,
ADD  `new_password` VARCHAR( 128 ) NOT NULL AFTER  `salt`;

UPDATE player SET salt = SHA1(RAND());

UPDATE player SET new_password = CONCAT(  'sha1$', player.salt,  '$', SHA1( CONCAT( player.salt, player.password ) ) );

INSERT INTO auth_user (username, first_name, last_name, email,
PASSWORD , is_staff, is_active, is_superuser, date_joined )
SELECT email, firstname, lastname, email, new_password,  '0',  '1',  '0', registered
FROM player;

ALTER TABLE  `player` ADD  `user_id` INT( 11 ) NOT NULL AFTER  `id`;

UPDATE player, auth_user SET player.user_id = auth_user.id WHERE player.email = auth_user.email;

UPDATE `player` SET player.id = player.user_id;

ALTER TABLE `player`
  DROP `password`,
  DROP `salt`,
  DROP `new_password`,
  DROP `firstname`,
  DROP `lastname`,
  DROP `registered`,
  DROP `email`,
  DROP `skills_id`;

ALTER TABLE  `player` DROP  `user_id`;

##################

ALTER TABLE  `attendance` DROP FOREIGN KEY  `attendance_ibfk_1` ;
ALTER TABLE  `attendance` CHANGE  `player_id`  `user_id` INT( 11 ) NULL DEFAULT NULL;
ALTER TABLE  `attendance` ADD FOREIGN KEY (  `user_id` ) REFERENCES  `auth_user` (
`id`
) ON DELETE CASCADE ON UPDATE CASCADE ;

ALTER TABLE  `registration` DROP FOREIGN KEY  `registration_ibfk_1` ;
ALTER TABLE  `registration` CHANGE  `player_id`  `user_id` INT( 11 ) NULL DEFAULT NULL;
ALTER TABLE  `registration` ADD FOREIGN KEY (  `user_id` ) REFERENCES  `auth_user` (
`id`
) ON DELETE CASCADE ON UPDATE CASCADE ;

ALTER TABLE  `score_report` DROP FOREIGN KEY  `score_report_ibfk_1` ;
ALTER TABLE  `score_report` ADD FOREIGN KEY (  `reported_by_id` ) REFERENCES  `auth_user` (
`id`
);

ALTER TABLE  `skills` DROP FOREIGN KEY  `skills_ibfk_2` ;
ALTER TABLE  `skills` DROP FOREIGN KEY  `skills_ibfk_3` ;
ALTER TABLE  `skills` CHANGE  `player_id`  `user_id` INT( 11 ) NULL DEFAULT NULL;
ALTER TABLE  `skills` ADD FOREIGN KEY (  `user_id` ) REFERENCES  `auth_user` (
`id`
) ON DELETE CASCADE ON UPDATE CASCADE ;
ALTER TABLE  `skills` ADD FOREIGN KEY (  `submitted_by_id` ) REFERENCES  `auth_user` (
`id`
) ON DELETE CASCADE ON UPDATE CASCADE ;

ALTER TABLE  `team_member` DROP FOREIGN KEY  `team_member_ibfk_2` ;
ALTER TABLE  `team_member` CHANGE  `player_id`  `user_id` INT( 11 ) NULL DEFAULT NULL;
ALTER TABLE  `team_member` ADD FOREIGN KEY (  `user_id` ) REFERENCES  `auth_user` (
`id`
) ON DELETE CASCADE ON UPDATE CASCADE ;

ALTER TABLE  `player` ADD FOREIGN KEY (  `id` ) REFERENCES  `auth_user` (
`id`
) ON DELETE CASCADE ON UPDATE CASCADE ;


ALTER TABLE  `attendance` CHANGE  `user_id`  `user_id` INT( 11 ) NOT NULL ,
CHANGE  `score_report_id`  `score_report_id` INT( 11 ) NOT NULL;

ALTER TABLE  `field` CHANGE  `name`  `name` TEXT CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL ,
CHANGE  `layout_link`  `layout_link` TEXT CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL ,
CHANGE  `address`  `address` TEXT CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL ,
CHANGE  `driving_link`  `driving_link` TEXT CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL ,
CHANGE  `note`  `note` TEXT CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL;

ALTER TABLE  `field_league` CHANGE  `league_id`  `league_id` INT( 11 ) NOT NULL ,
CHANGE  `field_id`  `field_id` INT( 11 ) NOT NULL;

ALTER TABLE  `field_names` CHANGE  `name`  `name` TEXT CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL ,
CHANGE  `field_id`  `field_id` INT( 11 ) NOT NULL;

ALTER TABLE  `game` CHANGE  `date`  `date` DATE NOT NULL ,
CHANGE  `field_name_id`  `field_name_id` INT( 11 ) NOT NULL ,
CHANGE  `schedule_id`  `schedule_id` INT( 11 ) NOT NULL;

ALTER TABLE `league` CHANGE `baggage` `baggage` INT(11) NOT NULL, CHANGE `night` `night` TEXT CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL, CHANGE `season` `season` TEXT CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL, CHANGE `year` `year` INT(11) NOT NULL, CHANGE `gender` `gender` TEXT CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL, CHANGE `gender_note` `gender_note` TEXT CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL, CHANGE `times` `times` TEXT CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL, CHANGE `reg_start_date` `reg_start_date` DATE NOT NULL, CHANGE `waitlist_start_date` `waitlist_start_date` DATE NOT NULL, CHANGE `freeze_group_date` `freeze_group_date` DATE NOT NULL, CHANGE `league_start_date` `league_start_date` DATE NOT NULL, CHANGE `league_end_date` `league_end_date` DATE NOT NULL, CHANGE `paypal_cost` `paypal_cost` INT(11) NOT NULL, CHANGE `check_cost` `check_cost` INT(11) NOT NULL;
ALTER TABLE  `league` CHANGE  `mail_check_address`  `mail_check_address` TEXT CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL ,
CHANGE  `field_id`  `field_id` INT( 11 ) NOT NULL ,
CHANGE  `max_players`  `max_players` INT( 11 ) NOT NULL ,
CHANGE  `state`  `state` VARCHAR( 32 ) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT  '',
CHANGE  `details`  `details` LONGTEXT CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL;

ALTER TABLE  `league_skip_dates` CHANGE  `league_id`  `league_id` INT( 11 ) NOT NULL ,
CHANGE  `skip_date`  `skip_date` DATE NOT NULL;

ALTER TABLE `player` CHANGE `groups` `groups` TEXT CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL, CHANGE `nickname` `nickname` TEXT CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL, CHANGE `phone` `phone` TEXT CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL, CHANGE `street_address` `street_address` TEXT CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL, CHANGE `city` `city` TEXT CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL, CHANGE `state` `state` CHAR(2) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL, CHANGE `zipcode` `zipcode` VARCHAR(5) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL, CHANGE `gender` `gender` CHAR(1) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL, CHANGE `height_inches` `height_inches` INT(11) NOT NULL, CHANGE `highest_level` `highest_level` TEXT CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL, CHANGE `birthdate` `birthdate` DATE NOT NULL;
ALTER TABLE  `player` CHANGE  `jersey_size`  `jersey_size` TEXT CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL;
ALTER TABLE  `player` CHANGE  `groups`  `groups` TEXT CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL ,
CHANGE  `nickname`  `nickname` VARCHAR( 30 ) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL ,
CHANGE  `phone`  `phone` VARCHAR( 15 ) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL ,
CHANGE  `street_address`  `street_address` VARCHAR( 255 ) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL ,
CHANGE  `city`  `city` VARCHAR( 127 ) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL ,
CHANGE  `jersey_size`  `jersey_size` VARCHAR( 15 ) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL;

ALTER TABLE  `registration` CHANGE  `status`  `status` TEXT CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL ,
CHANGE  `user_id`  `user_id` INT( 11 ) NOT NULL ,
CHANGE  `captaining`  `captaining` INT( 11 ) NOT NULL ,
CHANGE  `baggage_id`  `baggage_id` INT( 11 ) NOT NULL ,
CHANGE  `reg_time`  `reg_time` DATETIME NOT NULL ,
CHANGE  `attendance`  `attendance` INT( 11 ) NOT NULL;

ALTER TABLE  `schedule` CHANGE  `league_id`  `league_id` INT( 11 ) NOT NULL;

ALTER TABLE  `score_report` CHANGE  `reported_by_id`  `reported_by_id` INT( 11 ) NOT NULL ,
CHANGE  `us`  `us` INT( 11 ) NOT NULL ,
CHANGE  `them`  `them` INT( 11 ) NOT NULL ,
CHANGE  `spirit_score`  `spirit_score` INT( 11 ) NOT NULL ,
CHANGE  `game_id`  `game_id` INT( 11 ) NOT NULL ,
CHANGE  `comment`  `comment` TEXT CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL;

ALTER TABLE  `skills` CHANGE  `highest_level`  `highest_level` TEXT CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL ,
CHANGE  `athletic`  `athletic` INT( 11 ) NOT NULL ,
CHANGE  `experience`  `experience` INT( 11 ) NOT NULL ,
CHANGE  `forehand`  `forehand` INT( 11 ) NOT NULL ,
CHANGE  `backhand`  `backhand` INT( 11 ) NOT NULL ,
CHANGE  `receive`  `receive` INT( 11 ) NOT NULL ,
CHANGE  `strategy`  `strategy` INT( 11 ) NOT NULL ,
CHANGE  `position`  `position` INT( 11 ) NOT NULL ,
CHANGE  `skills_type_id`  `skills_type_id` INT( 11 ) NOT NULL ,
CHANGE  `user_id`  `user_id` INT( 11 ) NOT NULL ,
CHANGE  `submitted_by_id`  `submitted_by_id` INT( 11 ) NOT NULL ,
CHANGE  `updated`  `updated` DATE NOT NULL ,
CHANGE  `spirit`  `spirit` INT( 11 ) NOT NULL;
ALTER TABLE  `skills` ADD  `handle` INT( 11 ) NOT NULL AFTER `strategy`;
ALTER TABLE  `skills` ADD  `not_sure` BOOLEAN NOT NULL DEFAULT  '0';

ALTER TABLE  `skills_type` CHANGE  `description`  `description` TEXT CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL ,
CHANGE  `weight`  `weight` DOUBLE NOT NULL;

ALTER TABLE  `sponsor` CHANGE  `name`  `name` TEXT CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL ,
CHANGE  `image_small`  `image_small` TEXT CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL ,
CHANGE  `image_large`  `image_large` TEXT CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL ,
CHANGE  `address`  `address` TEXT CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL ,
CHANGE  `sponsor_link`  `sponsor_link` TEXT CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL ,
CHANGE  `map_link`  `map_link` TEXT CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL ,
CHANGE  `deal`  `deal` TEXT CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL ,
CHANGE  `phone_number`  `phone_number` TEXT CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL;

ALTER TABLE  `static_content` CHANGE  `url`  `url` VARCHAR( 255 ) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT  '',
CHANGE  `title`  `title` VARCHAR( 255 ) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT  '',
CHANGE  `content`  `content` LONGTEXT CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL;

ALTER TABLE  `static_nav_bar` CHANGE  `name`  `name` VARCHAR( 255 ) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT  '',
CHANGE  `content`  `content` LONGTEXT CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL;

ALTER TABLE  `team` CHANGE  `name`  `name` TEXT CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL ,
CHANGE  `color`  `color` TEXT CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL ,
CHANGE  `email`  `email` TEXT CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL ,
CHANGE  `league_id`  `league_id` INT( 11 ) NOT NULL;

ALTER TABLE  `team_member` CHANGE  `team_id`  `team_id` INT( 11 ) NOT NULL ,
CHANGE  `user_id`  `user_id` INT( 11 ) NOT NULL ,
CHANGE  `captain`  `captain` TINYINT( 4 ) NOT NULL;

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
CHANGE  `spirit`  `spirit` INT( 11 ) NOT NULL DEFAULT  '7',
CHANGE  `handle`  `handle` INT( 11 ) NOT NULL DEFAULT  '0';

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
