-- test_data

CREATE SCHEMA test;
CREATE TABLE test.data (
   id serial primary key,
   col1 int,
   col2 text,
   col3 text
)