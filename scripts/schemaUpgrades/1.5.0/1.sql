INSERT INTO schema_version (major, middle, minor) VALUES (1, 5, 1);

CREATE TABLE IF NOT EXISTS `league_new` (
	`id` int(11) NOT NULL AUTO_INCREMENT,
	`baggage` int(11) NOT NULL,
	`night` varchar(32) NOT NULL,
	`season` varchar(32) NOT NULL,
	`year` int(11) NOT NULL,
	`gender` varchar(32) NOT NULL,
	`gender_note` text NOT NULL,
	`times` text NOT NULL,
	`start_time` time NOT NULL,
	`end_time` time NOT NULL,
	`time_slots` int(3) NOT NULL,
	`reg_start_date` date NOT NULL,
	`waitlist_start_date` date NOT NULL,
	`freeze_group_date` date NOT NULL,
	`league_start_date` date NOT NULL,
	`league_end_date` date NOT NULL,
	`events_per_week` int(3) NOT NULL,
	`paypal_cost` int(11) NOT NULL,
	`check_cost` int(11) NOT NULL,
	`mail_check_address` text NOT NULL,
	`max_players` int(11) NOT NULL,
	`state` varchar(32) NOT NULL DEFAULT '',
	`details` longtext NOT NULL,
	`league_email` varchar(64) DEFAULT NULL,
	`league_captains_email` varchar(64) DEFAULT NULL,
	`division_email` varchar(64) DEFAULT NULL,
	PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 ;

INSERT INTO `league_new`
	SELECT
		`id`,
		`baggage`,
		`night`,
		`season`,
		`year`,
		`gender`,
		`gender_note`,
		`times`,
		'00:00:00',
		'00:00:00',
		1,
		`reg_start_date`,
		`waitlist_start_date`,
		`freeze_group_date`,
		`league_start_date`,
		`league_end_date`,
		1,
		`paypal_cost`,
		`check_cost`,
		`mail_check_address`,
		`max_players`,
		`state`,
		`details`,
		`league_email`,
		`league_captains_email`,
		`division_email`
	FROM `league`;


ALTER TABLE  `game` ADD  `league_id` INT( 11 ) NOT NULL ,
ADD INDEX (  `league_id` );

UPDATE `game`
JOIN `schedule` ON `schedule`.`id` = `game`.`schedule_id`
SET `game`.`league_id` = `schedule`.`league_id`;

ALTER TABLE  `game` ADD FOREIGN KEY (  `league_id` ) REFERENCES  `a2ultimate_build_2013_03_10`.`league` (
`id`
) ON DELETE RESTRICT ON UPDATE RESTRICT ;

DROP TABLE `schedule`;

