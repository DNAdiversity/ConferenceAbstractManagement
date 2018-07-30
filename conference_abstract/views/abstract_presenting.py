from cornice import Service
from pyramid.httpexceptions import HTTPForbidden, HTTPFound
import pyramid.security

import psycopg2
import psycopg2.extras

import os
import glob
import collections
import datetime

import valideer as V

import conference_abstract.util
import conference_abstract.app_dao
from conference_abstract.auth import User
import time
from conference_abstract.services.data.abstract_info import getAbstract,getAbstractFullDetails,getAbstractFullDetailsUnicode,getAbstractHistory
from conference_abstract.services.data.abstract_chair import getAbstractChairs
from conference_abstract.services.data.abstract_copyeditor import getAbstractEditors
from conference_abstract.services.data.abstract_topics import getCategories as getAbstractCategories
import unicodedata

info_desc = """\
This is the presenting author selection page
"""

service = Service(name='abstractPresenting', path='/abstract/{abstractId}/presenting', description=info_desc)

def getCategories():
    conn = conference_abstract.util.get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    sql = """select * from topics order by category, label;"""
    categories = []
    categoryNames = []
    currentCategory = 0
    cur.execute(sql)
    for row in cur.fetchall():
        categoryName = row['category']
        if categoryName not in categoryNames:
            currentCategory = len(categoryNames)
            categoryNames.append(categoryName)
            categories.append([])
        categories[currentCategory].append({"id":row["id"],"label":row["label"]})
    conn.close()
    return categories, categoryNames

def isAbstractInAgenda(abstractId):
    authors = []
    conn = conference_abstract.util.get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    sql = """select agenda.*, abstracts.title, abstract_type, abstract_text, abstract_text_edited, abstracts_presenting.created as assigned_date from agenda left join abstracts on agenda.fk_abstracts = abstracts.id left join abstracts_presenting on abstracts.id = abstracts_presenting.fk_abstracts where abstracts.id = %s;"""
    cur.execute(sql,[abstractId])
    if cur.rowcount < 1:
        return False,False
    else:
        row = cur.fetchone()
        print row["assigned_date"]
        if row["assigned_date"] is not None:
            return True, False
        else:
            abstract = {
                "id"    : row["fk_abstracts"],
                "title" : unicodedata.normalize('NFKD', row["title"].decode('unicode-escape')).encode('ascii', 'ignore'),
                "abstract_type"  : row["abstract_type"],
            }
            if row["abstract_text_edited"] is not None:
                abstract["abstract_text_edited"] = unicodedata.normalize('NFKD', row["abstract_text_edited"].decode('unicode-escape')).encode('ascii', 'ignore')
            else:
                abstract["abstract_text_edited"] = unicodedata.normalize('NFKD', row["abstract_text"].decode('unicode-escape')).encode('ascii', 'ignore')
            sqlAuthor = """select fk_abstract, fname || ' ' || mname || ' ' || lname as fullname, fname, mname, lname, corresponding, presenting, institution, department, address, country, email, id from authorship where fk_abstract=%s order by id asc"""
            print cur.mogrify(sqlAuthor,(abstractId,))
            cur.execute(sqlAuthor,(abstractId,))
            for row in cur.fetchall():
                abstractId = row["fk_abstract"]
                print "working on :",abstractId
                authors.append({
                    "id":row["id"],
                    "fullname":unicodedata.normalize('NFKD', row["fullname"].decode('unicode-escape')).encode('ascii', 'ignore'),
                    "first_name":unicodedata.normalize('NFKD', row["fname"].decode('unicode-escape')).encode('ascii', 'ignore'),
                    "middle_initial":unicodedata.normalize('NFKD', row["mname"].decode('unicode-escape')).encode('ascii', 'ignore'),
                    "last_name":unicodedata.normalize('NFKD', row["lname"].decode('unicode-escape')).encode('ascii', 'ignore'),
                    "corresponding":row["corresponding"],
                    "presenting":row["presenting"],
                    "institution":unicodedata.normalize('NFKD', row["institution"].decode('unicode-escape')).encode('ascii', 'ignore'),
                    "department":unicodedata.normalize('NFKD', row["department"].decode('unicode-escape')).encode('ascii', 'ignore'),
                    "address":unicodedata.normalize('NFKD', row["address"].decode('unicode-escape')).encode('ascii', 'ignore'),
                    "country":row["country"],
                    "email":row["email"]})
    return abstract, authors

def decodeID(abstractIdTemp):
    abstractId = int(float("%.17g" % abstractIdTemp)/1234567890*3.1415)
    print "*******>>>******"
    print abstractId,("%.17g" % abstractIdTemp)
    print "*******>>>******"
    #need to rounding to 15 places to make sure this is the correct one.
    if abstractId == float("%.13g" % (float("%.17g" % abstractIdTemp)/1234567890*3.1415)):
        return abstractId
    else:
        return 0

def encodeID(abstractID):
    return (abstractId/3.1415*1234567890)

@service.get()
def service_get(request):
    user = None
    abstract = None
    abstractAuthors = None
    reviewer = 0
    templateVars = {
        'user':None,
        'breadCrumbs':None,
        'pageTitle':'',
        'pageDesc':''
    }
    abstractIdEncoded = float("%.17g" % float(request.matchdict['abstractId']))
    idFix = {'336003675298.42426':855,'193349483329.6195983887': 492, '199637271405.3795776367': 508, '152085874082.4446716309': 387, '93923834381.6647949219': 239, '139903284685.6596984863': 356, '69951642342.8298492432': 178, '311245509750.1193237305': 792, '81741244984.8798217773': 208, '175272092611.8096313477': 446, '301027854127.0093383789': 766, '304564734919.6243286133': 775, '167019370762.3746337891': 425, '77811377437.5298309326': 198, '293561105787.0443725586': 747, '332466794505.8092651367': 846, '187061695253.8595886230': 476, '283343450163.9343872070': 721, '84885139022.7598114014': 216, '196100390612.7645874023': 499, '73488523135.4448394775': 187, '69165668833.3598480225': 176, '160731582686.6146545410': 409, '319498231599.5543212891': 813, '78597350946.9998321533': 200, '314782390542.7343139648': 801, '74274496644.9148406982': 189, '276269688578.7044067383': 703, '196886364122.2345886230': 501, '183131827706.5096435547': 466, '77418390682.7948455811': 197, '79383324456.4698486328': 202, '141082244949.8647155762': 359, '200423244914.8496093750': 510, '323035112392.1693725586': 822, '188633642272.7996215820': 480, '306136681938.5643920898': 779, '332073807751.0743408203': 845, '94316821136.3998107910': 240, '91565913853.2548217773': 233, '154836781365.5896911621': 394, '149727953554.0346984863': 381, '299455907108.0693969727': 762, '282164489899.7294311523': 718, '328536926958.4593505859': 836, '326571993184.7843627930': 831, '321070178618.4943847656': 817, '176844039630.7496337891': 450, '165054436988.6996765137': 420, '153264834346.6496887207': 390, '182345854197.0396423340': 464, '76632417173.3248443604': 195, '142654191968.8047180176': 363, '137545364157.2497253418': 350, '192170523065.4146118164': 489, '69558655588.0948638916': 177, '91172927098.5198211670': 232, '179594946913.8946533203': 457, '324607059411.1093750000': 826, '162303529705.5546875000': 413, '170556251554.9896545410': 434, '146191072761.4197082520': 372, '334431728279.4843139648': 851}
    if request.matchdict['abstractId'] in idFix:
        abstractId = idFix[request.matchdict['abstractId']]
    else:
        abstractId = decodeID(abstractIdEncoded)
    abstract, authors = isAbstractInAgenda(abstractId)
    print abstract, authors
    if abstract is not False:
        if authors is False:
            print "Updated"
            return conference_abstract.util.generate_template('abstractPresentingUpdated.mako',{})
        else:
            return conference_abstract.util.generate_template('abstractPresentingForm.mako',{
                'user': user,
                'breadCrumbs':[{"url":"/","text":"Home"},{"url":"","text":"Abstract "}],
                'abstract':abstract,
                'abstractIdEncoded':abstractIdEncoded,
                'authors':authors,
                'pageTitle':'',
                'pageDesc':'',
                'request':request 
           })
    else:
        templateVars["user"] = user
        return conference_abstract.util.generate_template('abstractNotFound.mako',templateVars)
    return conference_abstract.util.generate_template('noAccess.mako',templateVars)

@service.post()
def service_post(request):
    #Notes: Only can submit successful if nothing there already
    #record the ip address
    user = None
    presenterId = request.POST.get('presenter', None)
    abstractIdEncoded = request.matchdict['abstractId']
    idFix = {'336003675298.42426':855,'193349483329.6195983887': 492, '199637271405.3795776367': 508, '152085874082.4446716309': 387, '93923834381.6647949219': 239, '139903284685.6596984863': 356, '69951642342.8298492432': 178, '311245509750.1193237305': 792, '81741244984.8798217773': 208, '175272092611.8096313477': 446, '301027854127.0093383789': 766, '304564734919.6243286133': 775, '167019370762.3746337891': 425, '77811377437.5298309326': 198, '293561105787.0443725586': 747, '332466794505.8092651367': 846, '187061695253.8595886230': 476, '283343450163.9343872070': 721, '84885139022.7598114014': 216, '196100390612.7645874023': 499, '73488523135.4448394775': 187, '69165668833.3598480225': 176, '160731582686.6146545410': 409, '319498231599.5543212891': 813, '78597350946.9998321533': 200, '314782390542.7343139648': 801, '74274496644.9148406982': 189, '276269688578.7044067383': 703, '196886364122.2345886230': 501, '183131827706.5096435547': 466, '77418390682.7948455811': 197, '79383324456.4698486328': 202, '141082244949.8647155762': 359, '200423244914.8496093750': 510, '323035112392.1693725586': 822, '188633642272.7996215820': 480, '306136681938.5643920898': 779, '332073807751.0743408203': 845, '94316821136.3998107910': 240, '91565913853.2548217773': 233, '154836781365.5896911621': 394, '149727953554.0346984863': 381, '299455907108.0693969727': 762, '282164489899.7294311523': 718, '328536926958.4593505859': 836, '326571993184.7843627930': 831, '321070178618.4943847656': 817, '176844039630.7496337891': 450, '165054436988.6996765137': 420, '153264834346.6496887207': 390, '182345854197.0396423340': 464, '76632417173.3248443604': 195, '142654191968.8047180176': 363, '137545364157.2497253418': 350, '192170523065.4146118164': 489, '69558655588.0948638916': 177, '91172927098.5198211670': 232, '179594946913.8946533203': 457, '324607059411.1093750000': 826, '162303529705.5546875000': 413, '170556251554.9896545410': 434, '146191072761.4197082520': 372, '334431728279.4843139648': 851}
    if request.matchdict['abstractId'] in idFix:
        abstractId = idFix[request.matchdict['abstractId']]
    else:
        abstractId = decodeID(float(abstractIdEncoded))
    
    debug = True
    data = request.POST
    sqlList = []
    conn = conference_abstract.util.get_connection()
    cur = conn.cursor()
    sql = """insert into abstracts_presenting (fk_abstracts, fk_authorship, ip_address,created) values (%s,%s,%s,now()) RETURNING id;"""
    try:
        cur.execute(sql,[abstractId,presenterId,request.client_addr])
        if cur.rowcount == 1:
            result = cur.fetchone()
            #data = {"id":result[0],"abstractId":abstractId,"presenterId":presenterId,"ip":request.client_addr,"sql":sql}
            data = {"success":True}
            conn.commit()
            conn.close()
            nowTime = str(datetime.datetime.now())
            logFile = open("/tmp/updated.log","a")
            logFile.write(nowTime+"\t"+str(result)+"\t"+str(abstractId)+"\t"+str(presenterId)+"\t"+str(request.client_addr)+"\n")
            logFile.close();
            return conference_abstract.util.generate_response(data)
    except Exception as e:
        print ">>>>>>>>>> ERROR ERROR ERROR >>>>>>>>>>>>"
        print e
        print ">>>>>>>>>> ERROR ERROR ERROR >>>>>>>>>>>>"
    data = {"success":False}
    conn.close()
    return conference_abstract.util.generate_response(data)


