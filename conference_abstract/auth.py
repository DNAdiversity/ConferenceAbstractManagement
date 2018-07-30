#Change Log:
# 27 Mar 2017   Dean Chan   Added check for fk_cuser in the chair table
import urllib
import json
import hashlib
from pyramid.httpexceptions import HTTPForbidden
from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPNotFound
import pyramid.security
from pyramid.view import forbidden_view_config
from pyramid.view import view_config
import conference_abstract.util
import conference_abstract.app_dao
import psycopg2
import unicodedata

### DEFINE MODEL
class User(object):
    def __init__(self, login, password=None, groups=None):
        self.login = login
        self.userId = None
        self.fullname = None
        self.password = password
        self.groups = groups or []
        self.userLevel = None
        self.chairAccessKey = None
        self.chairId = None
        self.editorId = None

    def get_userLevel(self):
        return self.userLevel
    
    def is_admin(self):
        return self.userLevel == "admin"
    
    def is_reviewer(self):
        return self.userLevel == "reviewer"

    def is_editor(self):
        return self.userLevel == "editor"

    def check_userLevel(self):
        if self.userId in [90,478,479]:
            self.userLevel = "admin"
        if self.userId == 45:
            self.userLevel = "reviewer"
        if self.userId == 636:
            self.userLevel = "editor"
        ##adding another check for chair / reviewer
        #if self.check_reviewerID:
        #    self.userLevel = "reviewer"
        
    def check_reviewerID(self):
        conn = conference_abstract.util.get_connection()
        cur = conn.cursor()
        sql = """select accesskey from chairs where fk_cusers = %s """
        try:
            cur.execute(sql,[self.userId])
            if cur.rowcount == 1:
                return True
        except:
            pass
        return False
    
    def check_editorID(self):
        conn = conference_abstract.util.get_connection()
        cur = conn.cursor()
        sql = """select accesskey from copyeditor where fk_cusers = %s """
        try:
            cur.execute(sql,[self.userId])
            if cur.rowcount == 1:
                return True
        except:
            pass
        return False
    
    def check_password(self, passwd):
        result = self.checkDB(passwd)
        return result

    def checkDB(self, passwd):
        conn = conference_abstract.util.get_connection()
        cur = conn.cursor()
        sql = """select id from cusers where email=%s and password=%s;"""
        cur.execute(
            sql,
            (self.login, passwd))
        if cur.rowcount == 1:
            userId = cur.fetchone()[0]
            return userId
        else:
            return False

    def get_userObj(self):
        userObj = None
        if self.login is not None:
            conn = conference_abstract.util.get_connection()
            cur = conn.cursor()
            #sql = """select buser.id, person.fullname from buser left join person on buser.fk_person = person.id where buser.username = %s"""
            sql = """select id, first_name || ' ' || last_name as fullname from cusers where email = %s"""
            print self.login
            print cur.mogrify(sql,(self.login,))
            try:
                cur.execute(sql, (self.login,))
                #conn.commit()
                results = cur.fetchone()
                print results
                userObj = {"userId":results[0],"fullname":unicodedata.normalize('NFKD', results[1].decode('unicode-escape')).encode('ascii', 'ignore')}
                self.userId = results[0]
                self.fullname = results[1]
                self.check_userLevel
            except:
                print "Boom"
            conn.close()
        return userObj

    def get_chairObj(self,accessKey):
        userObj = None
        if self.login is not None:
            conn = conference_abstract.util.get_connection()
            cur = conn.cursor()
            sql = """select id, fullname, fk_cusers from chairs where accesskey = %s"""
            print cur.mogrify(sql,(accessKey,))
            try:
                cur.execute(sql,(accessKey,))
                if cur.rowcount == 0:
                    return False
                elif cur.rowcount == 1:
                    results = cur.fetchone()
                    self.chairId = results[0]
                    self.fullname = unicodedata.normalize('NFKD', results[1].decode('unicode-escape')).encode('ascii', 'ignore')
                    self.chairAccessKey = accessKey
                    self.userLevel = "reviewer"
                userObj = {"userId":self.userId,"chairId":self.chairId,"fullname":self.fullname}
            except:
                print "BOOOM!"
        return userObj

    def get_editorObj(self,accessKey):
        userObj = None
        if self.login is not None:
            conn = conference_abstract.util.get_connection()
            cur = conn.cursor()
            sql = """select id, fullname, fk_cusers from copyeditors where accesskey = %s"""
            print cur.mogrify(sql,(accessKey,))
            try:
                cur.execute(sql,(accessKey,))
                if cur.rowcount == 0:
                    return False
                elif cur.rowcount == 1:
                    results = cur.fetchone()
                    self.editorId = results[0]
                    self.fullname = unicodedata.normalize('NFKD', results[1].decode('unicode-escape')).encode('ascii', 'ignore')
                    self.chairAccessKey = accessKey
                    self.userLevel = "editor"
                userObj = {"userId":self.userId,"editorId":self.chairId,"fullname":self.fullname}
            except:
                print "BOOOM!"
        return userObj

    # not used as it doesn't use BOLD credentials
    def get_token(self,passwd):
        #test password with api server return True or False if we get the token
        apiURL = "http://131.104.63.24:6544/dropin/acl_gettoken"
        params = urllib.urlencode({'username': self.login, 'password': passwd})
        link = apiURL + "?%s" % params
        result = urllib.urlopen(link)
        isValid = False
        try:
            jsonResult = json.loads(result.read())
            if 'sessiontoken' in jsonResult:#anything else other than the token is invalid
                #TODO: do we add to session? currently we don't use other services so ok not to
                isValid = True
        except:
            # something bad happened so not valid try next type
            pass
        if isValid == True:
            return jsonResult['sessiontoken']
        else:
            return False

#return False or the user object
def check_user(request):
    login = pyramid.security.authenticated_userid(request)
    user = None
    isValid = False
    if login is not None:
        parseLogin = login.split("|")
        if len(parseLogin) == 2:
            username = parseLogin[0]
            userId = parseLogin[1]
            user = User(username)
            userObj = user.get_userObj()
        else:
            username = parseLogin[0]
            accessKey = parseLogin[1]
            user = User(username)
            user.get_userObj()
            userObj = user.get_chairObj(accessKey)
            if userObj == False:
                #check if it is an editor
                userObj = user.get_editorObj(accessKey)
        if userObj != False and userObj is not None:
            isValid = True
        #print "TESTING FOR SESSION",isValid
    if isValid == False:
        return False
    else:
        session = request.session
        #print session
        if 'fullname' in session:
            user.fullname = session["fullname"]
            user.userId = session["userId"]
            user.check_userLevel()
        else:
            session['fullname'] = userObj["fullname"]
            session['userId'] = userObj["userId"]
        return user

### DEFINE VIEWS
@forbidden_view_config()
def forbidden_view(request):
    # do not allow a user to login if they are already logged in
    if pyramid.security.authenticated_userid(request):
        return HTTPForbidden()

    loc = request.route_url('login', _query=(('next', request.path),))
    return HTTPFound(location=loc)


@view_config(
    route_name='logout',
)
def logout_view(request):
    headers = pyramid.security.forget(request)
    loc = request.route_url('home')
    return HTTPFound(location=loc, headers=headers)



@view_config(context=Exception, renderer='error.mako')
def error_view(context, request):
    login = pyramid.security.authenticated_userid(request)
    user = None
    if login is not None:
        username = login.split("|")[0]
        user = check_user(request)
    return {"user":user,"request":request}
'''
@view_config(
    route_name='reauth',
    renderer='json',
)
def reauth_view(request):
    login = pyramid.security.authenticated_userid(request)
    user = None
    isValid = False
    if login is not None:
        username = login.split("|")[0]
        token = login.split("|")[1]
        user = User(username)
        isValid = user.is_token_valid(token)
        print isValid
    return{
        'success':isValid,
    }
'''