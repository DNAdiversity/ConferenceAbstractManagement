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
This is the prize entry selection page
"""

service = Service(name='abstractPrizes', path='/abstract/{abstractId}/prizes', description=info_desc)

def isAbstractPoster(abstractId):
    #TODO: If we need all edited change the sql to check that the review_status = 'EDITED'
    authors = []
    conn = conference_abstract.util.get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    sql = """select abstracts.*, authorlist.all_authors, abstracts_prize_participation.participating from abstracts 
left join authorlist on authorlist.fk_abstract = abstracts.id
left join abstracts_prize_participation on abstracts_prize_participation.fk_abstracts = abstracts.id
where abstracts.id=%s"""
    cur.execute(sql,[str(abstractId)])
    if cur.rowcount < 1:
        return False
    else:
        row = cur.fetchone()
        abstract = {
            "id"    : row["id"],
            "title" : row["title"],
            "abstract_type" : row["abstract_type"],
            "authors" : row["all_authors"],
            "participating" : row["participating"]
        }
        if row["abstract_text_edited"] is not None:
            abstract["abstract_text_edited"] = row["abstract_text_edited"]
        else:
            abstract["abstract_text_edited"] = row["abstract_text"]
    return abstract

def isAbstractPosterLoggedIn(abstractId,submitterId):
    authors = []
    conn = conference_abstract.util.get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    sql = """select * from (
select * from 
(select abstracts.id, abstracts.title, abstract_type, abstract_text, abstract_text_edited, abstracts.abstract_attachment, authorlist.all_authors, abstracts.fk_submitter
from abstracts 
left join authorlist on authorlist.fk_abstract = abstracts.id
where abstract_type in ('Poster') and review_status = 'EDITED') as test
union
(select abstracts.id, abstracts.title, abstract_type, abstract_text, abstract_text_edited, abstracts.abstract_attachment, authorlist.all_authors, abstracts.fk_submitter from agenda 
left join abstracts on agenda.fk_abstracts = abstracts.id
left join authorlist on authorlist.fk_abstract = abstracts.id
where abstracts.abstract_type = 'Lightning Talk'
) ) as available_abstracts left join abstracts_prize_participation on available_abstracts.id = abstracts_prize_participation.fk_abstracts
where available_abstracts.id=%s and available_abstracts.fk_submitter = %s;""" #  
    cur.execute(sql,[abstractId,submitterId])
    if cur.rowcount < 1:
        return False
    else:
        row = cur.fetchone()
        abstract = {
            "id"    : row["id"],
            "title" : row["title"],
            "abstract_type" : row["abstract_type"],
            "authors" : row["all_authors"],
            "attachment" : row["abstract_attachment"]
        }
        if row["abstract_text_edited"] is not None:
            abstract["abstract_text_edited"] = row["abstract_text_edited"]
        else:
            abstract["abstract_text_edited"] = row["abstract_text"]
    return abstract

def encodeID(abstractID):
    a=(int(abstractID)*13)+111
    b=(int(abstractID)*17)+111
    return "%d.%d" % (a,b)
	


def decodeID(key):
    a,b=key.split(".")
    a=(int(a)-111)/13
    b=(int(b)-111)/17
    print "****************"
    print a,b
    print "****************"
    if a==b: return a
    return 0


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
    ##abstractIdEncoded = float("%.17g" % float(request.matchdict['abstractId']))
    abstractIdEncoded = request.matchdict['abstractId']
    # Below are the ids in the edited status that current get messed up results when you use the decode function this is a hard coded maping of the ones that didn't work
    idFix = {'178022999894.95462': 453, '119074986684.70476': 303, '167019370762.37463': 425, '62877880757.599869': 160, '215356741594.77954': 548, '104141490004.77478': 265, '175665079366.54465': 447, '208675966764.28455': 531, '81741244984.879822': 208, '329322900467.92932': 838, '153264834346.64969': 390, '334431728279.48431': 851, '160731582686.61465': 409, '279806569371.3194': 712, '166233397252.90463': 423, '125755761515.19974': 320, '152871847591.91467': 389, '113180185363.67976': 288, '116324079401.55975': 296, '85671112532.229828': 218, '146584059516.15469': 373, '216142715104.24954': 550, '260943205144.03946': 664, '252297496539.86948': 642, '211819860802.16455': 539, '216535701858.98456': 551, '202781165443.25958': 516, '135973417138.30972': 346, '321463165373.22931': 818, '123397840986.78973': 314, '180380920423.36462': 459, '190598576046.47458': 485, '80169297965.939835': 204, '84885139022.759811': 216, '179594946913.89465': 457, '270374887257.67941': 688, '235399066086.26453': 599, '282950463409.1994': 720, '334038741524.74927': 850, '124576801250.99475': 317, '106106423778.44978': 270, '213784794575.83957': 544, '318712258090.08435': 811, '87636046305.904816': 223, '86064099286.964828': 219, '332859781260.54431': 847, '121432907213.11475': 309, '110429278080.53477': 281, '157194701893.99966': 400, '220465569406.33453': 561, '176451052876.01462': 449, '235792052840.99948': 600, '65628788040.744865': 167, '328929913713.19427': 837, '79776311211.204834': 203, '206318046235.87457': 525, '182345854197.03964': 464, '232255172048.38449': 591, '139903284685.6597': 356, '321070178618.49438': 817, '145405099251.94971': 370, '314782390542.73431': 801, '123004854232.05473': 313, '283343450163.93439': 721, '254655417068.27948': 648, '214570768085.30957': 546, '112001225099.47478': 285, '263694112427.18445': 671, '189026629027.53461': 481, '200030258160.11459': 509, '125362774760.46474': 319, '187061695253.85959': 476, '74274496644.914841': 189, '293561105787.04437': 747, '106892397287.91978': 272, '132436536345.69472': 337, '155622754875.05966': 396, '76632417173.324844': 195, '75453456909.119843': 192, '199637271405.37958': 508, '244830748199.90448': 623, '157587688648.73468': 401, '144619125742.47971': 368, '137152377402.51471': 349, '196100390612.76459': 499, '277448648842.90942': 706, '103748503250.03979': 264, '248367628992.5195': 632, '326964979939.51929': 832, '287273317711.28442': 731, '225967383972.62451': 575, '146191072761.41971': 372, '248760615747.25449': 633, '331680820996.33936': 844, '243651787935.69949': 620, '300241880617.53937': 764, '214963754840.04453': 547, '286487344201.81439': 729, '230290238274.70953': 586, '164661450233.96466': 419, '57376066191.309875': 146, '69558655588.094864': 177, '77811377437.529831': 198, '130078615817.28474': 331, '91172927098.519821': 232, '154836781365.58969': 394, '262515152162.97946': 668, '98639675438.484787': 251, '156408728384.52966': 398, '195314417103.29459': 497, '265659046200.85944': 676, '150906913818.23969': 384, '136759390647.77972': 348, '107678370797.38977': 274, '244044774690.43448': 621, '307708628957.50433': 783, '93923834381.664795': 239, '311245509750.11932': 792, '109250317816.32977': 278, '115931092646.82477': 295, '159945609177.14465': 407, '320284205109.02435': 815, '246795681973.57947': 628, '97853701929.014801': 249, '75060470154.384842': 191, '290810198503.89941': 740, '163482489969.75964': 416, '171342225064.45966': 436, '301813827636.47937': 768, '145012112497.21469': 369, '227146344236.82953': 578, '239721920388.34949': 610, '332073807751.07434': 845, '117896026420.49974': 300, '69165668833.359848': 176, '172914172083.39963': 440, '120253946948.90974': 306, '67593721814.419853': 172, '339540556091.03925': 864, '192563509820.1496': 490, '129292642307.81473': 329, '210640900537.95956': 536, '77418390682.794846': 197, '301027854127.00934': 766, '170163264800.25464': 433, '303778761410.15436': 773, '60126973474.454872': 153, '176844039630.74963': 450, '196886364122.23459': 501, '315568364052.20435': 803, '78990337701.734833': 201, '95102794645.869812': 242, '134794456874.10472': 343, '58162039700.779877': 148, '273125794540.82443': 695, '132043549590.95972': 336, '231862185293.64954': 590, '154443794610.85468': 393, '324607059411.10938': 826, '134008483364.63472': 341, '198065324386.43958': 504, '111215251590.00476': 283, '193742470084.35458': 493, '297490973334.39435': 757, '218500635632.65955': 556, '176058066121.2796': 448, '175272092611.80963': 446, '80955271475.409836': 206, '135187443628.83971': 344, '222037516425.27454': 565, '69951642342.829849': 178, '217714662123.18954': 554, '240507893897.81949': 612, '188633642272.79962': 480, '62091907248.129875': 158, '112394211854.20978': 286, '160338595931.87967': 408, '183131827706.50964': 466, '280199556126.05438': 713, '322249138882.69934': 820, '145798086006.68469': 371, '323428099146.9043': 823, '64056841021.804871': 163, '319105244844.81934': 812, '66021774795.479858': 168, '315961350806.93933': 804, '81348258230.144821': 207, '63663854267.06987': 162, '190205589291.73962': 484, '333252768015.2793': 848, '296312013070.18939': 754, '158373662158.20468': 403, '152085874082.44467': 387, '124969788005.72974': 318, '323035112392.16937': 822, '180773907178.09961': 460, '120646933703.64474': 307, '336396662053.1593': 856, '79383324456.469849': 202, '141082244949.86472': 359, '246402695218.84448': 627, '221251542915.80457': 563, '209461940273.75458': 533, '196493377367.4996': 500, '221644529670.53952': 564, '261729178653.50946': 666, '207104019745.34457': 527, '284915397182.87439': 725, '195707403858.0296': 498, '87243059551.169815': 222, '249939576011.45947': 636, '116717066156.29475': 297, '329715887222.66431': 839, '306136681938.56439': 779, '304171748164.88934': 774, '231076211784.17953': 588, '325000046165.8443': 827, '153657821101.38467': 391, '193349483329.6196': 492, '191777536310.6796': 488, '174486119102.33963': 444, '314389403787.99933': 800, '91565913853.254822': 233, '80562284720.674835': 205, '73488523135.444839': 187, '102569542985.83478': 261, '67986708569.154861': 173, '297097986579.65936': 756, '143833152233.0097': 366, '299455907108.0694': 762, '142654191968.80472': 363, '134401470119.36972': 342, '336789648807.89429': 857, '151692887327.70969': 386, '335610688543.68933': 854, '203567138952.72958': 518, '102176556231.09978': 260, '270767874012.41443': 689, '240900880652.5545': 613, '277841635597.64441': 707, '147763019780.35968': 376, '266052032955.59445': 677, '227539330991.56454': 579, '118681999929.96976': 302, '322642125637.43433': 821, '169770278045.51962': 432, '126934721779.40474': 323, '315175377297.46936': 802, '274697741559.7644': 699, '258585284615.62946': 658, '64842814531.274864': 165, '188240655518.06461': 479, '310066549485.91437': 789, '91958900607.989807': 234, '328143940203.72437': 835, '137545364157.24973': 350, '335217701788.95428': 853, '181952867442.30463': 463, '78597350946.999832': 200, '63270867512.334862': 161, '222823489934.74454': 567, '336003675298.42426': 855, '140689258195.1297': 358, '122611867477.31975': 312, '323821085901.63934': 824, '235006079331.52951': 598, '306922655448.03436': 781, '276269688578.70441': 703, '143047178723.5397': 364, '121039920458.37976': 308, '94316821136.399811': 240, '205139085971.66956': 522}
    if request.matchdict['abstractId'] in idFix:
        abstractId = idFix[request.matchdict['abstractId']]
    else:
        abstractId = decodeID(abstractIdEncoded)
    abstract = isAbstractPoster(abstractId) ## change this function if you want more than just lightning talks in agenda and posters
    print abstract
    if abstract is not False:
        if abstract["participating"] is not None:
            templateVars = {
                "user": user,
                "title": "Abstract Updated",
                "message": "This abstract has already had prize entry selection selected. Please contact <a href='mailto:abstract@ibol.org'>abstract@ibol.org</a> if you want to change your selection."
            }
            return conference_abstract.util.generate_template('abstractThankYouMessage.mako',templateVars)
        else:
            return conference_abstract.util.generate_template('abstractPrizes.mako',{
                'user': user,
                'breadCrumbs':[{"url":"/","text":"Home"},{"url":"","text":"Abstract "}],
                'abstract':abstract,
                'abstractIdEncoded':abstractIdEncoded,
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
    participating = request.POST.get('participating', None)
    abstractIdEncoded = request.matchdict['abstractId']
    idFix = {'336003675298.42426':855,'193349483329.6195983887': 492, '199637271405.3795776367': 508, '152085874082.4446716309': 387, '93923834381.6647949219': 239, '139903284685.6596984863': 356, '69951642342.8298492432': 178, '311245509750.1193237305': 792, '81741244984.8798217773': 208, '175272092611.8096313477': 446, '301027854127.0093383789': 766, '304564734919.6243286133': 775, '167019370762.3746337891': 425, '77811377437.5298309326': 198, '293561105787.0443725586': 747, '332466794505.8092651367': 846, '187061695253.8595886230': 476, '283343450163.9343872070': 721, '84885139022.7598114014': 216, '196100390612.7645874023': 499, '73488523135.4448394775': 187, '69165668833.3598480225': 176, '160731582686.6146545410': 409, '319498231599.5543212891': 813, '78597350946.9998321533': 200, '314782390542.7343139648': 801, '74274496644.9148406982': 189, '276269688578.7044067383': 703, '196886364122.2345886230': 501, '183131827706.5096435547': 466, '77418390682.7948455811': 197, '79383324456.4698486328': 202, '141082244949.8647155762': 359, '200423244914.8496093750': 510, '323035112392.1693725586': 822, '188633642272.7996215820': 480, '306136681938.5643920898': 779, '332073807751.0743408203': 845, '94316821136.3998107910': 240, '91565913853.2548217773': 233, '154836781365.5896911621': 394, '149727953554.0346984863': 381, '299455907108.0693969727': 762, '282164489899.7294311523': 718, '328536926958.4593505859': 836, '326571993184.7843627930': 831, '321070178618.4943847656': 817, '176844039630.7496337891': 450, '165054436988.6996765137': 420, '153264834346.6496887207': 390, '182345854197.0396423340': 464, '76632417173.3248443604': 195, '142654191968.8047180176': 363, '137545364157.2497253418': 350, '192170523065.4146118164': 489, '69558655588.0948638916': 177, '91172927098.5198211670': 232, '179594946913.8946533203': 457, '324607059411.1093750000': 826, '162303529705.5546875000': 413, '170556251554.9896545410': 434, '146191072761.4197082520': 372, '334431728279.4843139648': 851}
    if request.matchdict['abstractId'] in idFix:
        abstractId = idFix[request.matchdict['abstractId']]
    else:
        abstractId = decodeID(abstractIdEncoded)
    
    debug = True
    data = request.POST
    sqlList = []
    conn = conference_abstract.util.get_connection()
    cur = conn.cursor()
    sql = """insert into abstracts_prize_participation (fk_abstracts, participating, ip_address,created) values (%s,%s,%s,now()) RETURNING id;"""
    try:
        cur.execute(sql,[abstractId,participating,request.client_addr])
        if cur.rowcount == 1:
            result = cur.fetchone()
            #data = {"id":result[0],"abstractId":abstractId,"presenterId":presenterId,"ip":request.client_addr,"sql":sql}
            data = {"success":True}
            conn.commit()
            conn.close()
            nowTime = str(datetime.datetime.now())
            logFile = open("/tmp/updatedPrize.log","a")
            logFile.write(nowTime+"\t"+str(result)+"\t"+str(abstractId)+"\t"+str(participating)+"\t"+str(request.client_addr)+"\n")
            logFile.close();
            return conference_abstract.util.generate_response(data)
    except Exception as e:
        print ">>>>>>>>>> ERROR ERROR ERROR >>>>>>>>>>>>"
        print e
        print ">>>>>>>>>> ERROR ERROR ERROR >>>>>>>>>>>>"
    data = {"success":False}
    conn.close()
    return conference_abstract.util.generate_response(data)


