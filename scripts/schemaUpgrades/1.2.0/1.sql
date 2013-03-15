INSERT INTO schema_version (major, middle, minor) VALUES (1, 2, 1);

# generate new game reports from old ones
INSERT INTO `game_report` (`team_id`, `game_id`, `last_updated_by_id`)
	SELECT `game_teams`.`team_id`, `score_report`.`game_id`, `score_report`.`reported_by_id`
	FROM `score_report`
	JOIN `game_teams` ON `game_teams`.`game_id` = `score_report`.`game_id`
	JOIN `team_member` ON `team_member`.`user_id` = `score_report`.`reported_by_id` AND `team_member`.`captain` = 1
	WHERE `game_teams`.`team_id` = `team_member`.`team_id`
	GROUP BY CONCAT(`score_report`.`game_id`, `game_teams`.`team_id`);
	
# populate new attendance	
INSERT INTO `game_report_attendance` (`report_id`, `user_id`)
	SELECT `game_report`.`id`, `attendance`.`user_id`
	FROM `attendance`
	JOIN `score_report` ON `score_report`.`id` = `attendance`.`score_report_id`
	JOIN `game_teams` ON `game_teams`.`game_id` = `score_report`.`game_id`
	JOIN `team_member` ON `team_member`.`user_id` = `score_report`.`reported_by_id` AND `team_member`.`captain` = 1
	JOIN `game_report` ON `game_report`.`game_id` = `score_report`.`game_id` AND `game_report`.`team_id` = `game_teams`.`team_id`
	WHERE `game_teams`.`team_id` = `team_member`.`team_id`
	GROUP BY CONCAT(`game_report`.`id`, `attendance`.`user_id`);

# populate game report comments
INSERT INTO `game_report_comment` (`report_id`, `submitted_by_id`, `spirit`, `comment`)
	SELECT `game_report`.`id`, `score_report`.`reported_by_id`, `score_report`.`spirit_score`, `score_report`.`comment`
	FROM `score_report`
	JOIN `game_teams` ON `game_teams`.`game_id` = `score_report`.`game_id`
	JOIN `team_member` ON `team_member`.`user_id` = `score_report`.`reported_by_id` AND `team_member`.`captain` = 1
	JOIN `game_report` ON `game_report`.`game_id` = `score_report`.`game_id` AND `game_report`.`team_id` = `game_teams`.`team_id`
	WHERE `game_teams`.`team_id` = `team_member`.`team_id` AND `score_report`.`spirit_score` > -1;
	
# populate game report scores
INSERT INTO `game_report_scores` (`report_id`, `team_id`, `score`)
	(SELECT `game_report`.`id` AS `report_id`, `game_teams`.`team_id` AS `team_id`, `score_report`.`us` AS `score`
	FROM `score_report`
	JOIN `game_teams` ON `game_teams`.`game_id` = `score_report`.`game_id`
	JOIN `team_member` ON `team_member`.`user_id` = `score_report`.`reported_by_id` AND `team_member`.`captain` = 1
	JOIN `game_report` ON `game_report`.`game_id` = `score_report`.`game_id` AND `game_report`.`team_id` = `game_teams`.`team_id`
	WHERE `game_teams`.`team_id` = `team_member`.`team_id` AND `score_report`.`spirit_score` > -1)
	UNION
	(SELECT `game_report`.`id` AS `report_id`, `game_teams`.`team_id` AS `team_id`, `score_report`.`them` AS `score`
	FROM `score_report`
	JOIN `game_teams` ON `game_teams`.`game_id` = `score_report`.`game_id`
	JOIN `team_member` ON `team_member`.`user_id` = `score_report`.`reported_by_id` AND `team_member`.`captain` = 1
	JOIN `game_report` ON `game_report`.`game_id` = `score_report`.`game_id` AND `game_report`.`team_id` = `game_teams`.`team_id`
	WHERE `game_teams`.`team_id` = `team_member`.`team_id` AND `score_report`.`spirit_score` > -1)
	ORDER BY `report_id`;
	
DROP TABLE  `attendance`,
`score_report`,
`static_nav_bar` ;
	