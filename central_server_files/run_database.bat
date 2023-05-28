docker run --name mysql -p 33060:3306 -d -e "MYSQL_ROOT_HOST=%" -e "MYSQL_ROOT_PASSWORD=1234" mysql
docker exec -it mysql bash

::mysql -u root -p
::1234
::CREATE DATABASE test;
::use test;
::CREATE TABLE data (id int, username varchar(255), password text, pos_x int, pos_y int, health int, strength int, resistance int, xp int, inventory json, PRIMARY KEY(id));
::CREATE TABLE id (current_id int);
::insert into id values(0);