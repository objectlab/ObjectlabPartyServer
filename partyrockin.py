import bottle
from beaker.middleware import SessionMiddleware
from bottle import route, run, template
from bottle import route, run, template, get, post, request, static_file, error, Bottle, redirect, abort, debug, response
from bottle import debug, Bottle
import simplejson as json
import MySQLdb as mdb
import sys
import hashlib
import copy
import os
import base64

userName = "cmollis"
password = "swordfi$h"
database = "partyrockin"
serverName = "localhost"

session_opts = {
    'session.type': 'file',
    'session.cookie_expires': True,
    'session.data_dir': './tmp',
    'session.auto': True
}

application = SessionMiddleware(bottle.default_app(), session_opts)

@route('/upload', method='POST')
def do_upload():
	responseObj = {}
	userid = request.forms.get('userid')
	upload = request.files.get('filename')
	randDir = base64.urlsafe_b64encode(os.urandom(10))

	name, ext = os.path.splitext(upload.filename)
	if ext not in ('.png','.jpg','.jpeg'):
		return "File extension not allowed."

	path_prefix = "/usr/share/nginx/www/"
        save_path = "images/{userid}/{directory_path}".format(userid=userid, directory_path=randDir)
	#save_path = "images/{userid}/{directory_path}".format(userid=userid, directory_path=randDir)
        #save_path = "./images/"
        full_path = path_prefix + save_path
	if not os.path.exists(full_path):
		os.makedirs(full_path)

	full_file_path = "{path}/{file}".format(path=full_path, file=upload.filename)
	url_file_path = "{path}/{file}".format(path=save_path, file=upload.filename)
        #upload.save(file_path)
	with open(full_file_path, 'w') as open_file:
		open_file.write(upload.file.read())

	#associate this file path with the user	

	try:
		con = mdb.connect(serverName, userName, password, database)
		cur = con.cursor(mdb.cursors.DictCursor)
		
		updateUser = "update USER set IMG_REF = %s where USER_ID = %s"
		cur.execute(updateUser, (url_file_path, userid) )	

		rows = cur.fetchall()

		if cur.rowcount > 0:
			responseObj["responseCd"] = 0
			responseObj["responseMsg"] = "User img_ref updated. File Save to {0}".format(full_file_path)
		else:
			responseObj["responseCd"] = 1
			responseObj["responseMsg"] = "User Not Found Error!";

	except mdb.Error, e:
			con.rollback()
			responseObj["responseCd"] = -1
			errMsg = "error occurred %d %s", (e.args[0], e.args[1] )
			responseObj["responseMsg"] = errMsg
	
	finally:
		if con:
			con.commit()
			con.close()	

        response.headers['Content-Type'] = 'application/json'	
	return json.dumps(responseObj) 

@route('/images/<filepath:path>')
def server_static(filepath):
	return static_file(filepath, root='./images')

@route('/')
def root():
    return static_file('test.html', root='.')

@route('/uploadimages')
def uploadimages():
	return static_file('imageform.html', root='.')

@route('/testclaim')
def testclaim():
        return static_file('testclaim.html', root='.')

@route('/testregister')
def testregister():
        return static_file('testregister.html', root='.')

@route('/testupdatename')
def testupdatename():
        return static_file('testupdatename.html', root='.')

@route('/deleteuser/<userId:int>')
def deleteuser(userId):
	responseObj = {}
	
	try:
		con = mdb.connect(serverName, userName, password, database)
		cur = con.cursor(mdb.cursors.DictCursor)

		deleteUser = "delete from USER where USER_ID = %s"
		cur.execute(deleteUser, (userId))

		rows = cur.fetchall()

		print "rows affected  %s" % cur.rowcount 

		if cur.rowcount > 0:
			responseObj["responseCd"] = 0
			responseObj["responseMsg"] = "User Deleted"
		else:
			responseObj["responseCd"] = 1
			responseObj["responseMsg"] = "User Not Found"
	
	except mdb.Error, e:
		con.rollback()
		responseObj["responseCd"] = -1
		errMsg = "error occurred %d %s", (e.args[0], e.args[1] )
		responseObj["responseMsg"] = errMsg	

	finally:
		if con:
			con.commit()
			con.close()

        response.headers['Content-Type'] = 'application/json'
	return json.dumps(responseObj)
		

@route('/users')
def users():
	responseObj = {}

	dataArray = []

	try:
		con = mdb.connect(serverName, userName, password, database)
		cur = con.cursor(mdb.cursors.DictCursor)

		allUsers = "select USER_ID, NAME, IMG_REF, BAR_SCORE, BEACON_1, BEACON_2, BEACON_3, BEACON_4, BEACON_5, BEACON_6, DATE_FORMAT(LAST_BAR_DETECTION, '%m/%d/%y %H:%i:%s') AS LAST_BAR_DETECTION, DATE_FORMAT(LAST_BEACON_CLAIM, '%m/%d/%y %H:%i:%s') AS LAST_BEACON_CLAIM, DEVICE_ID from USER"
		cur.execute(allUsers)

		rows = cur.fetchall()

		dataArray = copy.deepcopy(rows)
		responseObj["responseCd"] = 0
		responseObj["responseMsg"] = "all rows"
		responseObj["allUsers"] = dataArray

	except mdb.Error, e:
		con.rollback()
		responseObj["responseCd"] = -1
		errMsg = "error occurred %d %s", (e.args[0], e.args[1] )
		responseObj["responseMsg"] = errMsg	
	
	finally:
		if con:
			con.commit()
			con.close()	

	response.headers['Content-Type'] = 'application/json'
	return json.dumps(responseObj)
		

@route('/userreview')
def userreview():
        responseObj = {}

        try:
                con = mdb.connect(serverName, userName, password, database)
                cur = con.cursor(mdb.cursors.DictCursor)

                allUsers = "select USER_ID, NAME, IMG_REF, BAR_SCORE, (BEACON_1 + BEACON_2 + BEACON_3 + BEACON_4 + BEACON_5 + BEACON_6) as TOTAL_CLAIMS from USER"
                cur.execute(allUsers)

                rows = cur.fetchall()

                dataArray = copy.deepcopy(rows)

        except mdb.Error, e:
                con.rollback()
                responseObj["responseCd"] = -1
                errMsg = "error occurred %d %s", (e.args[0], e.args[1] )
                responseObj["responseMsg"] = errMsg

        finally:
                if con:
                        con.commit()
                        con.close()

        return template('userreview', rows=rows)

@route('/register', method='POST')
def register_user():
	responseObj = {}
	responseObj = {}
	dataObj = {}

        # JSON input
        device = request.json["device"]
        name = request.json["name"]

        # regular POST input
        #device = request.forms.get('device')
        #name = request.forms.get('name')

	try:
		con = mdb.connect(serverName, userName, password, database)
		cur = con.cursor(mdb.cursors.DictCursor)

		checkUser = "select USER_ID from USER where device_id = %s"
		cur.execute(checkUser, (device) )

		row = cur.fetchone()

		if row:
			responseObj["responseCd"] = 1
			responseObj["responseMsg"] = "user already exists"	
			responseObj["userId"] = (row["USER_ID"])
		else:
			#create this user 

			createUser = "insert into USER(NAME, DEVICE_ID) values (%s, %s)"
			cur.execute(createUser, (name, device) )

			rows = cur.fetchall()

			responseObj["responseCd"] = 0
			responseObj["responseMsg"] = "user created"
			responseObj["userId"] = (con.insert_id())

	except mdb.Error, e:
		con.rollback()
		responseObj["responseCd"] = -1
		errMsg = "error occurred %d %s", (e.args[0], e.args[1] )
		responseObj["responseMsg"] = errMsg 

	finally:
		if con:
			con.commit()
			con.close()

        response.headers['Content-Type'] = 'application/json'
	return json.dumps(responseObj)

@route('/update_name', method='POST')
def update_name():
        responseObj = {}
        responseObj = {}
        dataObj = {}

        # JSON input
        user_id = request.json["user_id"]
        name = request.json["name"]

        # regular POST input
        #user_id = request.forms.get('user_id')
        #name = request.forms.get('name')

        try:
                con = mdb.connect(serverName, userName, password, database)
                cur = con.cursor(mdb.cursors.DictCursor)

                updateUser = "update USER set NAME = '" + name + "' where USER_ID =" + user_id
                cur.execute(updateUser)

                rows = cur.fetchall()

                responseObj["responseCd"] = 0
                responseObj["responseMsg"] = "name updated"

        except mdb.Error, e:
                con.rollback()
                responseObj["responseCd"] = -1
                errMsg = "error occurred %d %s", (e.args[0], e.args[1] )
                responseObj["responseMsg"] = errMsg

        finally:
                if con:
                        con.commit()
                        con.close()

        response.headers['Content-Type'] = 'application/json'
        return json.dumps(responseObj)

@route('/leaderboard/<maxResults:int>')
def leaderboard(maxResults):
        responseObj = {}
        responseObj = {}
        dataObj = {}

        try:
                con = mdb.connect(serverName, userName, password, database)
                cur = con.cursor(mdb.cursors.DictCursor)

                leaderboard_1 = "select USER_ID, NAME, IMG_REF, BAR_SCORE from USER where BAR_SCORE > 0 order by BAR_SCORE desc LIMIT " + str(maxResults)

               	cur.execute(leaderboard_1)

                rows1 = cur.fetchall()

                dataArray1 = copy.deepcopy(rows1)
                responseObj["responseCd"] = 0
                responseObj["responseMsg"] = "leaders"
                responseObj["scoreLeaders"] = dataArray1

                leaderboard_2 = "select USER_ID, NAME, IMG_REF, (BEACON_1 + BEACON_2 + BEACON_3 + BEACON_4 + BEACON_5 + BEACON_6) as TOTAL_CLAIMS, DATE_FORMAT(LAST_BEACON_CLAIM, '%m/%d/%y %H:%i:%s') AS LAST_BEACON_CLAIM, BEACON_1, BEACON_2, BEACON_3, BEACON_4, BEACON_5, BEACON_6 from USER where (BEACON_1 + BEACON_2 + BEACON_3 + BEACON_4 + BEACON_5 + BEACON_6) > 0 order by (BEACON_1 + BEACON_2 + BEACON_3 + BEACON_4 + BEACON_5 + BEACON_6) desc, LAST_BEACON_CLAIM LIMIT " + str(maxResults)
                cur.execute(leaderboard_2)

                rows2 = cur.fetchall() 

                dataArray2 = copy.deepcopy(rows2) 
                responseObj["claimLeaders"] = dataArray2 

        except mdb.Error, e:
                con.rollback()
                responseObj["responseCd"] = -1
                errMsg = "error occurred %d %s", (e.args[0], e.args[1] )
                responseObj["responseMsg"] = errMsg

        finally:
                if con:
                        con.commit()
                        con.close()

        response.headers['Content-Type'] = 'application/json'
        return json.dumps(responseObj)

@route('/increment_bar_score/<user_id:int>')
def increment_bar_score(user_id):
        responseObj = {}
        responseObj = {}
        dataObj = {}

        try:
                con = mdb.connect(serverName, userName, password, database)
                cur = con.cursor(mdb.cursors.DictCursor)

                getCurScore = "select BAR_SCORE from USER where USER_ID = " + str(user_id)
                cur.execute(getCurScore)

                row = cur.fetchone()

                curScore = 0
                timestamp_phrase = ''
                if row:
                       	curScore  = int(row["BAR_SCORE"] + 1)
                        timestamp_phrase = ', LAST_BAR_DETECTION = CURRENT_TIMESTAMP' 
 
                        incrementScore = "update USER set BAR_SCORE = " + str(curScore) + timestamp_phrase + " where USER_ID = " + str(user_id)
                        cur.execute(incrementScore)

                        rows = cur.fetchall()

                responseObj["responseCd"] = 0
                responseObj["bar_score"] = curScore
                responseObj["responseMsg"] = "incremented"

        except mdb.Error, e:
                con.rollback()
                responseObj["responseCd"] = -1
                errMsg = "error occurred %d %s", (e.args[0], e.args[1] )
                responseObj["responseMsg"] = errMsg

        finally:
                if con:
                        con.commit()
                        con.close()

        response.headers['Content-Type'] = 'application/json'
        return json.dumps(responseObj)

@route('/claim', method='POST')
def claim():
        responseObj = {}
        responseObj = {}
        dataObj = {}

        # JSON input
        beacon_id = request.json["beacon_id"]
        user_id = request.json["user_id"]

        # regular POST input
        #beacon_id = request.forms.get('beacon_id')
        #user_id = request.forms.get('user_id')

        try:
                con = mdb.connect(serverName, userName, password, database)
                cur = con.cursor(mdb.cursors.DictCursor)

                getCurScore = "select BEACON_" + beacon_id + " as SCORE from USER where USER_ID = " + user_id
                cur.execute(getCurScore)

                row = cur.fetchone()

                curScore = 0
                timestamp_phrase = ''
                if row:
                        curScore  = int(row["SCORE"])
                        if curScore == 0:
                                 curScore = 1
                                 timestamp_phrase = ', LAST_BEACON_CLAIM = CURRENT_TIMESTAMP'

                                 incrementScore = "update USER set BEACON_" + beacon_id + " = " + str(curScore) + timestamp_phrase + " where USER_ID = " + user_id
                                 cur.execute(incrementScore)

                                 rows = cur.fetchall()

                responseObj["responseCd"] = 0
                responseObj["responseMsg"] = "claimed"

        except mdb.Error, e:
                con.rollback()
                responseObj["responseCd"] = -1
                errMsg = "error occurred %d %s", (e.args[0], e.args[1] )
                responseObj["responseMsg"] = errMsg

        finally:
                if con:
                        con.commit()
                        con.close()

        response.headers['Content-Type'] = 'application/json'
        return json.dumps(responseObj)

@route('/atbeacon/<maxResults:int>')
def atbeacon(maxResults):
        responseObj = {}
        responseObj = {}
        dataObj = {}

        try:
                con = mdb.connect(serverName, userName, password, database)
                cur = con.cursor(mdb.cursors.DictCursor)

                atbeacon = "select USER_ID, NAME, IMG_REF, BAR_SCORE, (BEACON_2 + BEACON_3 + BEACON_4 + BEACON_5 + BEACON_6 + BEACON_7 + BEACON_8) as TOTAL_CLAIMS, DATE_FORMAT(LAST_BAR_DETECTION, '%m/%d/%y %H:%i:%s') AS LAST_BAR_DETECTION from USER where BAR_SCORE > 0 order by LAST_BAR_DETECTION desc LIMIT " + str(maxResults)

                cur.execute(atbeacon)

                rows = cur.fetchall()

                dataArray = copy.deepcopy(rows)
                responseObj["responseCd"] = 0
                responseObj["responseMsg"] = "at beacon"
                responseObj["atBeacon"] = dataArray

        except mdb.Error, e:
                con.rollback()
                responseObj["responseCd"] = -1
                errMsg = "error occurred %d %s", (e.args[0], e.args[1] )
                responseObj["responseMsg"] = errMsg

        finally:
                if con:
                        con.commit()
                        con.close()

        response.headers['Content-Type'] = 'application/json'
        return json.dumps(responseObj)


@route('/hello/<name>')
def index(name='World'):

	beaker_session = request.environ['beaker.session']

	beaker_session['user_id'] = 10

	beaker_session.save()

    # Check to see if a value is in the session
    # Set some other session variable

	return template('<b>Hello {{name}}</b>!', name=name)

debug(True)

#if running from python..  'python partyrockin.py'     BLAH
#run(app=mainApp, server='gunicorn', host='0.0.0.0', port=8080, workers=20)

#if running from python, then this, otherwise this will run from the uwsgi container
if __name__ == "__main__":
	run(app=application, host='0.0.0.0', port=9080) 

#app = bottle.default_app()
