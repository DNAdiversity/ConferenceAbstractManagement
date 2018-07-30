from cornice import Service
from pyramid.httpexceptions import HTTPForbidden, HTTPFound
import pyramid.security
import uuid
import shutil

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
import unicodedata

info_desc = """\
This is the attachment upload page
"""

service = Service(name='abstractAttachmentUrl', path='/abstract/{abstractId}/attachmenturl', description=info_desc)


def isAbstractPoster(abstractId):
    authors = []
    conn = conference_abstract.util.get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    sql = """select abstracts.id, abstracts.title, abstract_type, abstract_text, abstract_text_edited, abstracts.abstract_attachment, authorlist.all_authors
        from abstracts left join authorlist on authorlist.fk_abstract = abstracts.id where abstract_type = 'Poster' and review_status = 'EDITED' and id=%s;""" # and abstract_attachment is null 
    cur.execute(sql,[abstractId])
    if cur.rowcount < 1:
        return False
    else:
        row = cur.fetchone()
        abstract = {
            "id"    : row["id"],
            "title" : unicodedata.normalize('NFKD', row["title"].decode('unicode-escape')).encode('ascii', 'ignore'),
            "abstract_type" : row["abstract_type"],
            "authors" : row["all_authors"],
            "attachment" : row["abstract_attachment"]
        }
        if row["abstract_text_edited"] is not None:
            abstract["abstract_text_edited"] = unicodedata.normalize('NFKD', row["abstract_text_edited"].decode('unicode-escape')).encode('ascii', 'ignore')
        else:
            abstract["abstract_text_edited"] = unicodedata.normalize('NFKD', row["abstract_text"].decode('unicode-escape')).encode('ascii', 'ignore')
    return abstract

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

def encodeID(abstractId):
    return "%.17g" % (int(abstractId)/3.1415*1234567890)

@service.get()
def service_get(request):
    user = None
    abstract = None
    abstractAuthors = None
    reviewer = 0
    data = {}
    templateVars = {
        'linkprefix':"http://abstracts.dnabarcodes2017.org/abstract/",
        'linksuffix':"/attachment",
        'code':''
    }
    if "encode" in request.GET:
        abstractIdEncoded = request.matchdict['abstractId']
        newCode = encodeID(abstractIdEncoded)
        print newCode
        templateVars["code"] = newCode
        print templateVars
        return conference_abstract.util.generate_template('link.mako',templateVars)
    else:
        abstractIdEncoded = float(request.matchdict['abstractId'])
        abstractId = decodeID(abstractIdEncoded)
        data["id"] = abstractId
        return conference_abstract.util.generate_response(data)
    '''
    abstractIdEncoded = float(request.matchdict['abstractId'])
    idFix = {'193349483329.6195983887': 492, '199637271405.3795776367': 508, '152085874082.4446716309': 387, '93923834381.6647949219': 239, '139903284685.6596984863': 356, '69951642342.8298492432': 178, '311245509750.1193237305': 792, '81741244984.8798217773': 208, '175272092611.8096313477': 446, '301027854127.0093383789': 766, '304564734919.6243286133': 775, '167019370762.3746337891': 425, '77811377437.5298309326': 198, '293561105787.0443725586': 747, '332466794505.8092651367': 846, '187061695253.8595886230': 476, '283343450163.9343872070': 721, '84885139022.7598114014': 216, '196100390612.7645874023': 499, '73488523135.4448394775': 187, '69165668833.3598480225': 176, '160731582686.6146545410': 409, '319498231599.5543212891': 813, '78597350946.9998321533': 200, '314782390542.7343139648': 801, '74274496644.9148406982': 189, '276269688578.7044067383': 703, '196886364122.2345886230': 501, '183131827706.5096435547': 466, '77418390682.7948455811': 197, '79383324456.4698486328': 202, '141082244949.8647155762': 359, '200423244914.8496093750': 510, '323035112392.1693725586': 822, '188633642272.7996215820': 480, '306136681938.5643920898': 779, '332073807751.0743408203': 845, '94316821136.3998107910': 240, '91565913853.2548217773': 233, '154836781365.5896911621': 394, '149727953554.0346984863': 381, '299455907108.0693969727': 762, '282164489899.7294311523': 718, '328536926958.4593505859': 836, '326571993184.7843627930': 831, '321070178618.4943847656': 817, '176844039630.7496337891': 450, '165054436988.6996765137': 420, '153264834346.6496887207': 390, '182345854197.0396423340': 464, '76632417173.3248443604': 195, '142654191968.8047180176': 363, '137545364157.2497253418': 350, '192170523065.4146118164': 489, '69558655588.0948638916': 177, '91172927098.5198211670': 232, '179594946913.8946533203': 457, '324607059411.1093750000': 826, '162303529705.5546875000': 413, '170556251554.9896545410': 434, '146191072761.4197082520': 372, '334431728279.4843139648': 851}
    if request.matchdict['abstractId'] in idFix:
        abstractId = idFix[request.matchdict['abstractId']]
    else:
        abstractId = decodeID(abstractIdEncoded)
    '''
    return conference_abstract.util.generate_response(data)

