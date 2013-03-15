create table schema_version ( major int NOT NULL, middle int NOT NULL, minor int NOT NULL );
insert into schema_version( major, middle, minor ) VALUES ( 1, 1, 0 );