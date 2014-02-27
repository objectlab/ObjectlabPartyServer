Objectlab Party Server : Installation
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

