import json
import sys
import time
import urllib

import psycopg2
from pyramid.response import Response
from pyramid.renderers import render
from mako.template import Template
from mako.lookup import TemplateLookup

import smtplib
from email.mime.text import MIMEText
from uuid import uuid4
import random

# Helpers
def generate_template(templateName, data):
    resp = Response(render('/var/www/conference_abstract/conference_abstract/templates/'+templateName, data))
    #respTemplate = ('/var/www/conference_abstract/conference_abstract/templates/'+templateName)
    #print respTemplate.render_unicode(template_args=data)
    
    resp.headerlist.append(('Access-Control-Allow-Origin', '*'))
    resp.content_type = 'text/html; charset=utf-8'
    resp.charset = "utf-8"

    return resp

def generate_response(data):
    resp = Response()
    resp.body = json.dumps(data)
    resp.headerlist.append(('Access-Control-Allow-Origin', '*'))
    resp.content_type = 'application/javascript; charset=utf-8'
    return resp

def generate_text_response(data):
    resp = Response()
    resp.body = str(data)
    resp.headerlist.append(('Access-Control-Allow-Origin', '*'))
    resp.content_type = 'text/plain; charset=utf-8'
    return resp

def generate_tsv_response(data,filename):
    resp = Response()
    resp.body = str(data)
    resp.headerlist.append(('Access-Control-Allow-Origin', '*'))
    resp.content_type = 'application/vnd.ms-excel; charset=utf-8-sig'
    resp.content_disposition = 'attachment; filename=%s' % filename
    return resp

def generate_xlsx_response(data,filename):
    resp = Response()
    resp.body = data
    resp.headerlist.append(('Access-Control-Allow-Origin', '*'))
    resp.content_type = 'application/vnd.ms-excel; charset=utf-8-sig'
    resp.content_disposition = 'attachment; filename=%s' % filename
    return resp


def get_connection(token='ngs_api_prod'):
    """Return an instantiated psycopg2 connection object to the
    db associated to the token"""
    if token == 'ngs_api_prod':
        dsn = "host='127.0.0.1' dbname='conference_abstracts1' user='postgres' password='%s'"
    else:
        params = urllib.urlencode({'token': token})
        dbconn = json.load(urllib.urlopen("http://192.168.12.66/DBManager/get_connection?%s" % params))
        dsn = "host='" +str(dbconn['server']) +"' dbname='" +str(dbconn['db']) +"' user='" +str(dbconn['user']) +"' password='%s'"

    conn = psycopg2.connect(dsn)

    return conn


def seqlen(seq):
    return len(seq)


def log(token, step, message):
    print >> sys.stderr, "NGS\t{}\t{}\t{}\t{}".format(token, time.time(), step, message)

def jsonify(multiDict):
    jsonOut = {}
    for key in multiDict:
        if key not in jsonOut:
            jsonOut[key] = multiDict.getall(key)
            if len(jsonOut[key]) == 1:
                jsonOut[key] = jsonOut[key][0]
    return jsonOut

def sendMail(senderEmail,targetEmail,subject,messageBody):
    msg = MIMEText(messageBody)
    msg['Subject'] = subject
    msg['From'] = senderEmail
    msg['To'] = ",".join(targetEmail)
    msg['reply-to'] = 'abstracts@ibol.org'
    msg.add_header('reply-to', 'abstracts@ibol.org')
    # Send the message via our own SMTP server, but don't include the
    # envelope header.
    #s = smtplib.SMTP('mail.uoguelph.ca')
    #s.sendmail(senderEmail, targetEmail, msg.as_string())
    #s.quit()
    usernames = ['abstracts@ibol.org','abstractsadmin@ibol.org','abstractsmanager@ibol.org']
    passwords = ['carrots007','kruger2017!','acdb2017!']
    whichEmail = random.randrange(0,99) % 3
    username = usernames[whichEmail]
    password = passwords[whichEmail]
    server = smtplib.SMTP()
    server.connect('smtp.gmail.com',587)
    server.ehlo()
    server.starttls()
    server.login(username,password)
    server.sendmail(senderEmail, targetEmail, msg.as_string())
    server.quit()
    f = open("/tmp/"+str(uuid4())+".txt","w")
    f.write(username)
    f.write(msg.as_string())
    f.close()
