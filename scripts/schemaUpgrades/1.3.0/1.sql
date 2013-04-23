INSERT INTO schema_version (major, middle, minor) VALUES (1, 3, 1);

CREATE TABLE IF NOT EXISTS `registrations` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `league_id` int(11) NOT NULL,
  `baggage_id` int(11) NULL DEFAULT NULL,
  `created` datetime NOT NULL,
  `updated` datetime NOT NULL,
  `registered` datetime NULL DEFAULT NULL,
  `conduct_complete` BOOLEAN NOT NULL DEFAULT 0,
  `waiver_complete` BOOLEAN NOT NULL DEFAULT 0,
  `pay_type` ENUM('check', 'paypal') NULL DEFAULT NULL,
  `check_complete` BOOLEAN NOT NULL DEFAULT 0,
  `paypal_invoice_id` VARCHAR(127) NULL DEFAULT NULL,
  `paypal_complete` BOOLEAN NOT NULL DEFAULT 0,
  `refunded` BOOLEAN NOT NULL DEFAULT 0,
  `waitlist` BOOLEAN NOT NULL DEFAULT 0,
  `attendance` int(2) NULL DEFAULT NULL,
  `captain` int(2) NULL DEFAULT NULL,
  `guardian` BOOLEAN NULL DEFAULT NULL,
  `guardian_name` VARCHAR(255) NULL DEFAULT NULL,
  `guardian_email` VARCHAR(255) NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `league_id` (`league_id`),
  KEY `player_id` (`user_id`),
  KEY `baggage_id` (`baggage_id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8;

ALTER TABLE `registrations`
  ADD CONSTRAINT `registrations_ibfk_1` FOREIGN KEY (`league_id`) REFERENCES `league` (`id`) ON DELETE SET NULL ON UPDATE SET NULL,
  ADD CONSTRAINT `registrations_ibfk_2` FOREIGN KEY (`baggage_id`) REFERENCES `baggage` (`id`) ON DELETE SET NULL ON UPDATE SET NULL,
  ADD CONSTRAINT `registrations_ibfk_3` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;


INSERT INTO `registrations` (`id`, `user_id`, `league_id`, `baggage_id`, `created`, `updated`, `conduct_complete`, `waiver_complete`, `pay_type`, `check_complete`, `paypal_invoice_id`, `paypal_complete`, `waitlist`, `attendance`, `captain`, `guardian`, `guardian_name`, `guardian_email`)

SELECT
NULL,
user_id,
league_id,
baggage_id,
reg_time,
reg_time,
reg_time,
status NOT IN ('new'),
status NOT IN ('new', 'clicked_waiver'),
IF(status LIKE '%paypal%', 'paypal', IF(status LIKE '%check%', 'check', NULL)),
status IN ('check_completed', 'check-completed_waitlist'),
NULL,
status IN ('paypal_completed', 'paypal-completed_waitlist'),
status LIKE '%waitlist%',
attendance,
captaining,
`guardian_waiver`,
`guardian_name`,
`guardian_email`
FROM registration
WHERE league_id != 0;

DROP TABLE registration;