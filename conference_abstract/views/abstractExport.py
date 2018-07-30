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

info_desc = """\
This is the home page for brave
"""


countryCodes="""
Afghanistan|AF
ALA|Aland Islands
Albania|AL
Algeria|DZ
American Samoa|AS
Andorra|AD
Angola|AO
Anguilla|AI
Antarctica|AQ
Antigua and Barbuda|AG
Argentina|AR
Armenia|AM
Aruba|AW
Australia|AU
Austria|AT
Azerbaijan|AZ
Bahamas|BS
Bahrain|BH
Bangladesh|BD
Barbados|BB
Belarus|BY
Belgium|BE
Belize|BZ
Benin|BJ
Bermuda|BM
Bhutan|BT
Bolivia|BO
Bosnia and Herzegovina|BA
Botswana|BW
Bouvet Island|BV
Brazil|BR
British Virgin Islands|VG
British Indian Ocean Territory|IO
Brunei Darussalam|BN
Bulgaria|BG
Burkina Faso|BF
Burundi|BI
Cambodia|KH
Cameroon|CM
Canada|CA
Cape Verde|CV
Cayman Islands|KY
Central African Republic|CF
Chad|TD
Chile|CL
China|CN
Hong Kong, SAR China|HK
Macao, SAR China|MO
Christmas Island|CX
Cocos (Keeling) Islands|CC
Colombia|CO
Comoros|KM
Congo (Brazzaville)|CG
Congo, (Kinshasa)|CD
Cook Islands|CK
Costa Rica|CR
Cote d'Ivoire|CI
Croatia|HR
Cuba|CU
Cyprus|CY
Czech Republic|CZ
Denmark|DK
Djibouti|DJ
Dominica|DM
Dominican Republic|DO
Ecuador|EC
Egypt|EG
El Salvador|SV
Equatorial Guinea|GQ
Eritrea|ER
Estonia|EE
Ethiopia|ET
Falkland Islands (Malvinas)|FK
Faroe Islands|FO
Fiji|FJ
Finland|FI
France|FR
French Guiana|GF
French Polynesia|PF
French Southern Territories|TF
Gabon|GA
Gambia|GM
Georgia|GE
Germany|DE
Ghana|GH
Gibraltar|GI
Greece|GR
Greenland|GL
Grenada|GD
Guadeloupe|GP
Guam|GU
Guatemala|GT
Guernsey|GG
Guinea|GN
Guinea-Bissau|GW
Guyana|GY
Haiti|HT
Heard and Mcdonald Islands|HM
Holy See (Vatican City State)|VA
Honduras|HN
Hungary|HU
Iceland|IS
India|IN
Indonesia|ID
Iran, Islamic Republic of|IR
Iraq|IQ
Ireland|IE
Isle of Man|IM
Israel|IL
Italy|IT
Jamaica|JM
Japan|JP
Jersey|JE
Jordan|JO
Kazakhstan|KZ
Kenya|KE
Kiribati|KI
Korea (North)|KP
Korea (South)|KR
Kuwait|KW
Kyrgyzstan|KG
Lao PDR|LA
Latvia|LV
Lebanon|LB
Lesotho|LS
Liberia|LR
Libya|LY
Liechtenstein|LI
Lithuania|LT
Luxembourg|LU
Macedonia, Republic of|MK
Madagascar|MG
Malawi|MW
Malaysia|MY
Maldives|MV
Mali|ML
Malta|MT
Marshall Islands|MH
Martinique|MQ
Mauritania|MR
Mauritius|MU
Mayotte|YT
Mexico|MX
Micronesia, Federated States of|FM
Moldova|MD
Monaco|MC
Mongolia|MN
Montenegro|ME
Montserrat|MS
Morocco|MA
Mozambique|MZ
Myanmar|MM
Namibia|NA
Nauru|NR
Nepal|NP
Netherlands|NL
Netherlands Antilles|AN
New Caledonia|NC
New Zealand|NZ
Nicaragua|NI
Niger|NE
Nigeria|NG
Niue|NU
Norfolk Island|NF
Northern Mariana Islands|MP
Norway|NO
Oman|OM
Pakistan|PK
Palau|PW
Palestinian Territory|PS
Panama|PA
Papua New Guinea|PG
Paraguay|PY
Peru|PE
Philippines|PH
Pitcairn|PN
Poland|PL
Portugal|PT
Puerto Rico|PR
Qatar|QA
Reunion|RE
Romania|RO
Russian Federation|RU
Rwanda|RW
Saint-Barthelemy|BL
Saint Helena|SH
Saint Kitts and Nevis|KN
Saint Lucia|LC
Saint-Martin (French part)|MF
Saint Pierre and Miquelon|PM
Saint Vincent and Grenadines|VC
Samoa|WS
San Marino|SM
Sao Tome and Principe|ST
Saudi Arabia|SA
Senegal|SN
Serbia|RS
Seychelles|SC
Sierra Leone|SL
Singapore|SG
Slovakia|SK
Slovenia|SI
Solomon Islands|SB
Somalia|SO
South Africa|ZA
South Georgia and the South Sandwich Islands|GS
South Sudan|SS
Spain|ES
Sri Lanka|LK
Sudan|SD
Suriname|SR
Svalbard and Jan Mayen Islands|SJ
Swaziland|SZ
Sweden|SE
Switzerland|CH
Syrian Arab Republic (Syria)|SY
Taiwan, Republic of China|TW
Tajikistan|TJ
Tanzania, United Republic of|TZ
Thailand|TH
Timor-Leste|TL
Togo|TG
Tokelau|TK
Tonga|TO
Trinidad and Tobago|TT
Tunisia|TN
Turkey|TR
Turkmenistan|TM
Turks and Caicos Islands|TC
Tuvalu|TV
Uganda|UG
Ukraine|UA
United Arab Emirates|AE
United Kingdom|GB
United States of America|US
US Minor Outlying Islands|UM
Uruguay|UY
Uzbekistan|UZ
Vanuatu|VU
Venezuela (Bolivarian Republic)|VE
Viet Nam|VN
Virgin Islands, US|VI
Wallis and Futuna Islands|WF
Western Sahara|EH
Yemen|YE
Zambia|ZM
Zimbabwe|ZW
"""

countryCodeDict={}
for country in countryCodes.strip().split("\n"):
    name,code=country.split("|")
    countryCodeDict[code]=name

service = Service(name='abstractExport', path='/abstractExport', description=info_desc)

@service.get()
def service_get(request):
    
    conn = conference_abstract.util.get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    out=['<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd"> <html lang="en"> <head> <meta http-equiv="content-type" content="text/html; charset=utf-8"> <title>Title Goes Here</title> </head><body>']
    
    abstracts=[]
    sql = """Select abstracts.id as id,abstract_type, review_status, title, abstract_text_edited,score from abstracts inner join abstracts_score on (fk_abstracts=abstracts.id) where score=4 and review_status='EDITED' and length(abstract_text_edited)>10  and abstract_type='Talk' order by abstract_type"""
    cur.execute(sql)
    abstracts=cur.fetchall()
    
    for i in range (len(abstracts)):
        sql="select fname,mname,lname,corresponding,email,department,institution,country from authorship where fk_abstract="+str(abstracts[i]["id"])+" order by author_rank"
        cur.execute(sql)
        authors=cur.fetchall()
        authorList=[]
        affiliations={}

        correspondingEmail=None
        for author in authors:
            if author["mname"]==None or len(author["mname"])<1: author["mname"]=""
            else: author["mname"]=author["mname"][0]
            
            aff=[]
            for key in ("department","institution","country"):
                if key=="country": author[key]=countryCodeDict.get(author[key],author[key])
                if author[key]!=None and len(author[key])>1: aff.append(author[key])
            aff=", ".join(aff)
            if len(aff)<2: aff="UNSPECIFIED"
            
            if not affiliations.has_key(aff): affiliations[aff]=len(affiliations)
           
            a=author["fname"]+" "+author["mname"]+" "+author["lname"]
            if author["corresponding"] and correspondingEmail==None:
                authorList.append(a.replace("  "," ").replace("  "," ")+"<sup>"+str(affiliations[aff]+1)+"</sup>"+"<sup>*</sup>")
                correspondingEmail=author["email"]
                
            else: authorList.append(a.replace("  "," ").replace("  "," ")+"<sup>"+str(affiliations[aff]+1)+"</sup>")
            
        if correspondingEmail==None:
            correspondingEmail=authors[0]["email"]
            authorList[0]+="<sup>*</sup>"
        
        affiliationTable={}
        for aff,rank in affiliations.items(): affiliationTable[int(rank)]=aff
        
        authors=", ".join(authorList)
        
        sql="select editor_category,editor_supercategory from abstracts_score where editor_category is not null and fk_abstracts="+str(abstracts[i]["id"])
        cur.execute(sql)
        category=cur.fetchall()
        
        if len(category)>0: category=category[0]["editor_category"]+" ("+category[0]["editor_supercategory"]+")"
        else: category="Unspecified"
        
        abstracts[i]["authors"]=authors
        abstracts[i]["category"]=category
        abstracts[i]["affiliations"]=affiliationTable
        abstracts[i]["correspondingEmail"]=correspondingEmail
    
    
    for abstract in abstracts:
        
        affiliations=abstract["affiliations"]
        correspondingEmail=abstract["correspondingEmail"]
        for key in abstract.keys(): abstract[key]=str(abstract[key])
        strout=[]
        
    
      
        strout.append("<h4>"+"ID: "+str(abstract["id"])+"&nbsp;&nbsp;&nbsp;&nbsp;CATEGORY: "+str(abstract["category"])+"&nbsp;&nbsp;&nbsp;&nbsp;TYPE: "+str(abstract["abstract_type"])+"</h4>")
        
        strout.append("<br>")
        
        strout.append("<h3>"+abstract["title"]+"</h3>")
        strout.append(abstract["authors"])
        strout.append("<br>")
        strout.append("<br>")
        strout.append("<em>")
        for i in range(len(affiliations)):
            aff=affiliations[i]
            strout.append("<sup>"+str(i+1)+"</sup>"+aff+"; ")
        strout.append("</em>")
        strout.append("<br>")
        strout.append("<br>")
        if correspondingEmail!=None: strout.append("<em>*Email:"+correspondingEmail+"</em>")
        strout.append("<br>")
        #strout.append("<p>"+abstract["abstract_text_edited"]+"</p>")
        strout.append("<br>")
        strout.append("<hr />")
        out.append("<section>"+ "".join(strout)+"</section>")
    
    out.append('</body> </html>')
    
    print "\n\n\n\n#########################\n\n"
    print "<br><br>".join(out)
    print "\n\n\n\n#########################\n\n"
    
    return len(abstracts)
        
    return conference_abstract.util.generate_template('abstractList.mako',{"user":user,"request":request})

