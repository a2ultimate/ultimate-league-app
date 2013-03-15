INSERT INTO schema_version (major, middle, minor) VALUES (1, 3, 1);

CREATE TABLE IF NOT EXISTS `registrations` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `league_id` int(11) NOT NULL,
  `baggage_id` int(11) NULL DEFAULT NULL,
  `created` datetime NOT NULL,
  `updated` datetime NOT NULL,
  `conduct_complete` BOOLEAN NOT NULL DEFAULT 0,
  `waiver_complete` BOOLEAN NOT NULL DEFAULT 0,
  `pay_type` ENUM('check', 'paypal') NULL DEFAULT NULL,
  `check_complete` BOOLEAN NOT NULL DEFAULT 0,
  `paypal_invoice_id` VARCHAR(127) NULL DEFAULT NULL,
  `paypal_complete` BOOLEAN NOT NULL DEFAULT 0,
  `waitlist` BOOLEAN NOT NULL DEFAULT 0,
  `attendance` int(2) NULL DEFAULT NULL,
  `captain` int(2) NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `league_id` (`league_id`),
  KEY `player_id` (`user_id`),
  KEY `baggage_id` (`baggage_id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8;

ALTER TABLE `registrations`
  ADD CONSTRAINT `registrations_ibfk_1` FOREIGN KEY (`league_id`) REFERENCES `league` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `registrations_ibfk_2` FOREIGN KEY (`baggage_id`) REFERENCES `baggage` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `registrations_ibfk_3` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;