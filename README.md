Objectlab Tommy Server : Installation
============
The 'party server' does just that: it serves the party, dude.  Not the Party (in the Bolshevik sense), but *the Par-tay.*

Actually, it handles things like:
  
* User Registration
* Image Upload
* Beacon 'Claiming'
* Bar Score Updating

Version
--
1.0

Installation
------------
The server has only been tested on *nix (specifically Ubuntu), but should work with any Python 2.6+ installation.
  
First you need to have Python installation.  
Next big item, mysql.
  
Next, you need to set up Bottle.

http://bottlepy.org/docs/dev/index.html

Bottle dependencies:

```
 pip install mysql-python
 pip intall bottle-mysql
 pip install beaker
 pip install simplejson
```

Installing mysql:

```
sudo apt-get install mysql-server mysql-client.
```

If you get mysql errors connect errors, check your dynamic link path. Something like:

```
MYSQL=/usr/local/mysql/bin
export PATH=$PATH:$MYSQL
export DYLD_LIBRARY_PATH=/usr/local/mysql/lib:$DYLD_LIBRARY_PATH
```

Creating the database:
--

Once you get mysql installed, you should create a new database (or you can just use the default.  It won't matter because there is only one table.)

```
create database <insert db name here>;
use database <insert db name here>;
```

Now you can create the table schema:

```
CREATE TABLE USER (
  USER_ID int(11) NOT NULL AUTO_INCREMENT,
  NAME varchar(255) NOT NULL DEFAULT '',
  IMG_REF varchar(255) DEFAULT NULL,
  BAR_SCORE int(11) NOT NULL DEFAULT '0',
  BEACON_1 int(11) NOT NULL DEFAULT '0',
  BEACON_2 int(11) NOT NULL DEFAULT '0',
  BEACON_3 int(11) NOT NULL DEFAULT '0',
  BEACON_4 int(11) NOT NULL DEFAULT '0',
  BEACON_5 int(11) NOT NULL DEFAULT '0',
  BEACON_6 int(11) NOT NULL DEFAULT '0',
  BEACON_7 int(11) NOT NULL DEFAULT '0',
  BEACON_8 int(11) NOT NULL DEFAULT '0',
  FOUND_EGGS int(11) NOT NULL DEFAULT '0',
  LAST_BAR_DETECTION timestamp NULL DEFAULT NULL,
  LAST_BEACON_CLAIM timestamp NULL DEFAULT NULL,
  DEVICE_ID varchar(255) DEFAULT '',
  UNIQUE KEY `USER_ID` (`USER_ID`)
);
```

NEXT:  UWSGI set up... 