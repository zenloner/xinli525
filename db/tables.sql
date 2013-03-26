drop table if exists paper;

CREATE TABLE paper (
	paper_id int primary key auto_increment,
	title text,
	description text,
	content text
)

CREATE TABLE user (
	user_id int primary key auto_increment,
	username varchar(50),
	password varchar(50),
	email varchar(50)
)

CREATE TABLE topic (
	id int primary key auto_increment,
	author varchar(50),
	title text,
	content text,
	ctime datetime,
	mtime datetime
)

alter table topic change title title text

CREATE TABLE reply (
	id int primary key auto_increment,
	author varchar(50),
	content text,
	mtime datetime,
	tid int,
	foreign key (tid) references topic(id)
	on delete cascade
)


CREATE TABLE test (
	id int primary key auto_increment,
	title text,
	filename varchar(50),
	mtime datetime
)
