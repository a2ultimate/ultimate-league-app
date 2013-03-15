INSERT INTO schema_version (major, middle, minor) VALUES (1, 4, 1);

ALTER TABLE  `player` ADD  `signature` LONGTEXT CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL ,
ADD  `signature_html` LONGTEXT CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL ,
ADD  `time_zone` DOUBLE NOT NULL ,
ADD  `language` VARCHAR( 10 ) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL ,
ADD  `show_signatures` TINYINT( 1 ) NOT NULL ,
ADD  `post_count` INT( 11 ) NOT NULL ,
ADD  `avatar` VARCHAR( 100 ) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL ,
ADD  `autosubscribe` TINYINT( 1 ) NOT NULL;