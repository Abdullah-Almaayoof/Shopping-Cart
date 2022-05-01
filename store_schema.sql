-- PRAGMA foreign_keys=off;

DROP TABLE IF EXISTS product;
CREATE TABLE product (
  prodid        int(6) not null PRIMARY KEY,
  image         varchar(50) not null,
  name          varchar(50) not null,
  price         double(50) not null,
  quantity      int(5),
  catid         int(5) not null,
  FOREIGN KEY(catid) REFERENCES category(catid)
);

DROP TABLE IF EXISTS customer;
CREATE TABLE customer (
  custid          int(5) not null PRIMARY KEY,
  username        varchar(50) not null,
  password        varchar(50) not null,
  fname           varchar(50) not null,
  lname           varchar(50) not null
);

DROP TABLE IF EXISTS cart;
CREATE TABLE cart (
  custid          int(5) not null,
  prodid          int(6) not null,
  specificid      int(6) not null,
  FOREIGN KEY(custid) REFERENCES customer(custid),
	FOREIGN KEY(prodid) REFERENCES product(prodid)
);

DROP TABLE IF EXISTS category;
CREATE TABLE category (
  catid          int(5) not null PRIMARY KEY,
  name           varchar(50) not null
);

-- PRAGMA foreign_keys=on;

-- product
INSERT INTO product VALUES ('123456', 'apples.jpg', 'Apples', '2.99', '76', 1);
INSERT INTO product VALUES ('612345', 'bananas.jpg', 'Bananas', '2.99', '34', 1);
INSERT INTO product VALUES ('713456', 'icecream.jpg', 'Ice Cream', '3.59', '103', 2);
INSERT INTO product VALUES ('134564', 'oranges.jpg', 'Oranges', '2.99', '44', 1);
INSERT INTO product VALUES ('145321', 'grapes.jpg', 'Grapes', '3.25', '123', 1); 
INSERT INTO product VALUES ('136543', 'cheese.jpg', 'Cheese', '5.99', '77', 2);
INSERT INTO product VALUES ('147638', 'cherries.jpg', 'Cherries', '3.99', '15', 1);
INSERT INTO product VALUES ('164732', 'milk.jpg', 'Milk', '5.95', '25', 2);
INSERT INTO product VALUES ('176463', 'salmon.jpg', 'Salmon Fish', '11.99', '17', 3);
INSERT INTO product VALUES ('164733', 'chicken.jpg', 'Chicken', '10.99', '9', 3); 
INSERT INTO product VALUES ('164753', 'steak.jpg', 'Ribeye Steak', '12.99', '1', 3); 

-- customer
INSERT INTO customer VALUES ('72527', 'testuser', 'testpass', 'test', 'test');
INSERT INTO customer VALUES ('73012', 'Almayoof', 'pass', 'Abdullah', 'Almaayoof');
INSERT INTO customer VALUES ('15382', 'mfrank', 'pass', 'Frank', 'Malone');
INSERT INTO customer VALUES ('54921', 'gwashington', 'pass', 'George', 'Washington');
INSERT INTO customer VALUES ('72518', 'timwood', 'pass', 'Tim', 'Wood'); 

-- category
INSERT INTO category VALUES(1, 'Fruits');
INSERT INTO category VALUES(2, 'Dairy');
INSERT INTO category VALUES(3, 'Meats');