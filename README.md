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

[http://bottlepy.org/docs/dev/index.html]

Some useful Bottle dependencies that we utilized:

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

Once you have everything installed, it's a good idea to test your python-to-MySQL connection..  You can open a Python session and type the following:

```
import MySQLdb as mdb
con = mdb.connect(<your serverName>, <your db userName>, <your db password>, <your db database>)
```
If it doesn't throw an exception, you're good to go.

If you do get mysql errors connect errors, check your dynamic link path. Something like:

```
MYSQL=/usr/local/mysql/bin
export PATH=$PATH:$MYSQL
export DYLD_LIBRARY_PATH=/usr/local/mysql/lib:$DYLD_LIBRARY_PATH
```

###Creating the database:


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

###Deployment:
  
  
Bottle is a great little wsgi app server that ships with 
its own HTTP server.  This is fine for testing, but I didn't think it would hold together with more than a few people using it.  Both the iPhone app and the D3.js visualization make a lot of server requests so we needed a more scaleable container than the default server.
  
####UWSGI

UWSGI supports pre-forked, multi-threaded access to Python applications that conform to the WSGI standard.  (more information here: [http://uwsgi-docs.readthedocs.org/en/latest/](http://uwsgi-docs.readthedocs.org/en/latest/ "UWSGI Homepage")

You can run the UWSGI container in a bunch of different ways, but we settled on the following for our deployment:

```
uwsgi --http :9080 --wsgi-file /home/cmollis/partyrockin/partyrockin.py --master --processes 20 --threads 4


//This command runs the bottle app on port 9080 with 20 pre-forked processes; 4 connection threads per process.
```

Now that we have a performant container for our application, we should put a performant web server in front of it.

####NGINX
Finally, we installed NGINX on port 80 and locked down all of the other ports on the AWS instance.   We wanted to use NGINX to reverse-proxy to the UWSGI instance, but also serve up any images and static files (like user images taken with their phones, and the D3.js visualization).

There is a lot of web collateral on how to set up NGINX as a reverse-proxy:

 [http://www.howtoforge.com/how-to-set-up-nginx-as-a-reverse-proxy-for-apache2-on-ubuntu-12.04]
 
Here is an excerpt from our server configuration:

```
server {
        #listen   80; ## listen for ipv4; this line is default and implied
        #listen   [::]:80 default ipv6only=on; ## listen for ipv6

        root /usr/share/nginx/www;
        index index.html index.htm;

        # Make site accessible from http://localhost/
        server_name localhost;

        location @proxy {

                proxy_pass http://localhost:9080;
                include /etc/nginx/proxy_params;
        }

        location / {
                # First attempt to serve request as file, then
                # as directory, then fall back to index.html
                #try_files $uri $uri/ /index.html;
                # Uncomment to enable naxsi on this location
                # include /etc/nginx/naxsi.rules

                try_files $uri @proxy;
        }

        location ~* \.(js|css|jpg|jpeg|gif|png|svg|ico|pdf|html|htm)$ {
       }

        location /doc/ {
                alias /usr/share/doc/;
                autoindex on;
                allow 127.0.0.1;
                deny all;
        }
```



