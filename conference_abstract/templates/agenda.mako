<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<!--[if IE 9]> <html class="ie9"> <![endif]-->
<!--[if !IE]><!--> <html> <!--<![endif]-->
<% 
	dayReplace = {'Day 1':'Day 1 - Tuesday, 21st November 2017','Day 2':'Day 2 - Wednesday, 22nd November 2017','Day 3':'Day 3 - Thursday, 23rd November 2017','Day 4':'Day 4 - Friday, 24th November 2017'}
%>
<head>
	<meta charset="utf-8">
	<title>Conference Abstracts: International Barcode of Life 2017</title>
	<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, minimum-scale=1.0, user-scalable=no">
	<meta name="apple-mobile-web-app-capable" content="yes">
	<meta name="apple-touch-fullscreen" content="yes">
	<meta name="description" content="7th annual DNA">
	<link rel="stylesheet" href="/static/css/bootstrap.min.css">
<style>
h1,.h1,
h2,.h2,
h3,.h3,
h4,.h4,
h5,.h5,
h6,.h6 {
	font-family:Arial, sans-serif;
	font-weight: 700;
	line-height:1;
	color:#303030;
	margin-top:0;
}
h2,
.h2{
	font-size:24px;
	margin-bottom:20px;
}

h5{
	margin-bottom: 0px;
	font-size:12px;
}
hr{
	margin-top: 5px;
	margin-bottom: 5px;
}
section{
	padding-bottom: 5px;
	padding-top:10px;
	border-bottom: 5px solid #030303;
	padding-left:10px;
	padding-right:10px;
	margin-bottom:10px;
	margin-top:0px;
}
td.side{
	padding-bottom: 5px;
	padding-left:5px;
	border-bottom:8px solid #fff;
}
td.content{
	vertical-align: top;
}
small.presenting{
	font-size:9px;
}
@media print {
	section.pagebreak {page-break-after: always;}
}
</style>
	<link rel="stylesheet" href="/static/css/override.css">
</head>
<body>

<div id="content" role="main">
	<div class="container">
	<div class="row">
		<div class="col-sm-12">
				

				<h2 class="title-border custom mb40">Agenda</h2>
				
				<h3>Plenary Sessions</h3>
				<div style="padding-left:10px;">
				% if len(agendas) > 0:
				##Plenary
				<% 
					counter = 0 
					sectionCounter = 0
					currentSection = ""
					currentBackground = 0
					##backgroundColours = ["#945115","#A86E21","#B47E27","#C0902D","#C8A034","#ABAD47","#96BA58","#87C66E","#7CD795","#78CEA1","#74C4AD","#70BBB8"]
					##backgroundColours = ['#7CD795', '#C0902D', '#C8A034', '#78CEA1', '#74C4AD', '#945115', '#70BBB8', '#87C66E', '#A86E21', '#96BA58', '#ABAD47', '#B47E27']
					##backgroundColours = ['#f1fbf4','#dddeaf','#e9d9ac','#e8f7ef','#dff2ec','#e89d5a','#d8eceb','#e2f1dc','#e5b87d','#dae7c4','#dddeaf','#e6c48e']
					backgroundColours = ['#efefef','#ebeccc']
				%>
					% for agenda in agendas:
						% if "plenary" in agenda["session_id"].lower():
						<% checkSection = str(agenda["date_time"])+str(agenda["room_name"]) %>
						% if checkSection != currentSection:
							<% 
								sectionCounter += 1
								currentSection = checkSection 
								currentBackground += 1
								if currentBackground > len(backgroundColours)-1:
									currentBackground = 0
							%>
							% if counter > 0:
				</section>
<!--		</td></tr></table>-->
							% endif
<!--				<table width>
					<tr>
						<td></td>
						<td style="width:100%">-->
						<%
						roomName = agenda["room_name"].split("|")
						parseDay = agenda["date_time"].split("-",1)
						displayDay = agenda["date_time"]
						if parseDay[0].strip() in dayReplace:
							displayDay = dayReplace[parseDay[0].strip()]+" -"+parseDay[1]
						%>
						% if "plenary" in agenda["session_id"].lower():
						<strong>${displayDay}</strong>, ${roomName[1]}<br/>
							% if agenda["chair"] != "" and agenda["chair"] != "TBD":
							${agenda["session_id"]}, Chair: ${agenda["chair"]}
							% else:
							${agenda["session_id"]}
							% endif
						% else:
						<strong>${agenda["date_time"]}</strong>, ${roomName[1]}<br/>
							% if agenda["chair"] != "" and agenda["chair"] != "TBD":
							${agenda["session_id"]} - ${agenda["session_name"]}, Chair: ${agenda["chair"]}
							% else:
							${agenda["session_id"]} - ${agenda["session_name"]}
							% endif
						% endif
<!--						</td>
				</tr>
				<tr>-->
				## if "plenary" in agenda["session_id"].lower():
<!--				<td class="side" style="width:22px;background-color:${backgroundColours[currentBackground]};vertical-align: middle;"><img src="/static/images/PLENARY_image.png" style="height:100px;" alt="Plenary"/></td>-->
				## else:
				<!--<td class="side" style="width:22px"><img style="width:21px;height:1px;" src="/static/images/blank.png"/></td>-->
					
				## endif
				<!--<td class="content">-->
				% if sectionCounter > 4:
				<section class="pagebreak" style="background-color:${backgroundColours[currentBackground]}">
				% else:
				<section style="background-color:${backgroundColours[currentBackground]}">
				% endif
						% else:
							% if counter > 0:
<!--					<div class="mb20"></div> space -->
					<hr/>
							% endif
						% endif
				<div class="row">
					<div class="col-sm-12 mb0-xs">
							% if agenda["abstract_id"] is not None:
								<h5>${agenda["title"].decode('utf-8')}</h5>
								##${agenda["abstract_type"]}
								##${agenda["abstract_text"].decode('utf-8')}
								##${agenda["abstract_text_edited"].decode('utf-8')}
								##<small class="presenting">${agenda["authors"].decode('utf-8')}</small><br/>
								% if agenda["presenter_id"] is not None:
								<%
									##allIds = ""
									presentingAuthor = agenda["presenter_id"]
									if agenda["abstract_id"] in authors:
										for author in authors[agenda["abstract_id"]]:
											##allIds += " "+author["id"]
											if author["id"] == agenda["presenter_id"]:
												presentingAuthor = author["fullname"]
								%>
								##<small class="presenting">Presenting: ${presentingAuthor.decode('utf-8')}</small>
								<small class="presenting">${presentingAuthor.decode('utf-8')}</small>
								% else:
									% if agenda["abstract_id"] in authors:
										% if len(authors[agenda["abstract_id"]]) > 0:
										<%
										authorText = "author"
										if len(authors[agenda["abstract_id"]]) > 1:
											authorText = "authors"
										%>
								##<small>Presenting: <u>${authors[agenda["abstract_id"]][0]["fullname"].decode('utf-8')} (${authors[agenda["abstract_id"]][0]["email"]}, ${len(authors[agenda["abstract_id"]])} ${authorText})**</u></small>
								<small><u>${authors[agenda["abstract_id"]][0]["fullname"].decode('utf-8')} (<a href="mailto:${authors[agenda["abstract_id"]][0]["email"]}">${authors[agenda["abstract_id"]][0]["email"]}</a>)**</u></small>
										% else:
								##<small>Presenting: <u>No Authors ***</u></small>
								<small>Presenting: <u>No Authors ***</u></small>
										% endif
									% else:
								##<small>Presenting: <u>No Authors ***</u></small>
								<small><u>No Authors ***</u></small>
									% endif
								% endif
							% else:
								<h5>No Title</h5>
							% endif
					</div><!-- End .col-sm-12 -->
				</div><!-- End .row -->
					<% counter += 1 %>
						% endif
					% endfor
				</section>
				</div><!-- end left padding -->
				<div style="padding:20px;"></div>
				<h3>Parallel Sessions</h3>
				<div style="padding-left:10px;">
				##Parallel
				<% 
					counter = 0 
					sectionCounter = 0
					currentSection = ""
					currentBackground = 0
					##backgroundColours = ["#945115","#A86E21","#B47E27","#C0902D","#C8A034","#ABAD47","#96BA58","#87C66E","#7CD795","#78CEA1","#74C4AD","#70BBB8"]
					##backgroundColours = ['#7CD795', '#C0902D', '#C8A034', '#78CEA1', '#74C4AD', '#945115', '#70BBB8', '#87C66E', '#A86E21', '#96BA58', '#ABAD47', '#B47E27']
					##backgroundColours = ['#f1fbf4','#dddeaf','#e9d9ac','#e8f7ef','#dff2ec','#e89d5a','#d8eceb','#e2f1dc','#e5b87d','#dae7c4','#dddeaf','#e6c48e']
					backgroundColours = ['#efefef','#ebeccc']
				%>
					% for agenda in agendas:
						% if "plenary" not in agenda["session_id"].lower():
						<% 
							checkSection = str(agenda["date_time"])+str(agenda["room_name"]) 
						%>
						% if checkSection != currentSection:
							<% 
								sectionCounter += 1
								currentSection = checkSection 
								currentBackground += 1
								if currentBackground > len(backgroundColours)-1:
									currentBackground = 0
							%>
							% if counter > 0:
				</section>
							% endif
						<%
						roomName = agenda["room_name"].split("|")
						parseDay = agenda["date_time"].split("-",1)
						displayDay = agenda["date_time"]
						if parseDay[0].strip() in dayReplace:
							displayDay = dayReplace[parseDay[0].strip()]+" -"+parseDay[1]
						
						%>
						<strong>${displayDay}</strong>, ${roomName[1]}<br/>
							% if agenda["chair"] != "" and agenda["chair"] != "TBD":
							${agenda["session_id"]} - ${agenda["session_name"]}, Chair: ${agenda["chair"]}
							% else:
							${agenda["session_id"]} - ${agenda["session_name"]}
							% endif
							## ${sectionCounter} <!-- UNCOMMENT if we need to figure out the repagination -->
				% if sectionCounter in [5,10,13,17,21,26,31,36,41]:
				<section class="pagebreak" style="background-color:${backgroundColours[currentBackground]}">
				% else:
				<section style="background-color:${backgroundColours[currentBackground]}">
				% endif
						% else:
							% if counter > 0:
<!--					<div class="mb20"></div> space -->
					<hr/>
							% endif
						% endif
				<div class="row">
					<div class="col-sm-12 mb0-xs">
							% if agenda["abstract_id"] is not None:
								<h5>${agenda["title"].decode('utf-8')}</h5>
								##${agenda["abstract_type"]}
								##${agenda["abstract_text"].decode('utf-8')}
								##${agenda["abstract_text_edited"].decode('utf-8')}
								##<small class="presenting">${agenda["authors"].decode('utf-8')}</small><br/>
								% if agenda["presenter_id"] is not None:
								<%
									##allIds = ""
									presentingAuthor = agenda["presenter_id"]
									if agenda["abstract_id"] in authors:
										for author in authors[agenda["abstract_id"]]:
											##allIds += " "+author["id"]
											if author["id"] == agenda["presenter_id"]:
												presentingAuthor = author["fullname"]
								%>
								##<small class="presenting">Presenting: ${presentingAuthor.decode('utf-8')}</small>
								<small class="presenting">${presentingAuthor.decode('utf-8')}</small>
								% else:
									% if agenda["abstract_id"] in authors:
										% if len(authors[agenda["abstract_id"]]) > 0:
										<%
										authorText = "author"
										if len(authors[agenda["abstract_id"]]) > 1:
											authorText = "authors"
										%>
								##<small>Presenting: <u>${authors[agenda["abstract_id"]][0]["fullname"].decode('utf-8')} (${authors[agenda["abstract_id"]][0]["email"]}, ${len(authors[agenda["abstract_id"]])} ${authorText})**</u></small>
								<small><u>${authors[agenda["abstract_id"]][0]["fullname"].decode('utf-8')} (<a href="mailto:${authors[agenda["abstract_id"]][0]["email"]}">${authors[agenda["abstract_id"]][0]["email"]}</a>)**</u></small>
										% else:
								##<small>Presenting: <u>No Authors ***</u></small>
								<small>Presenting: <u>No Authors ***</u></small>
										% endif
									% else:
								##<small>Presenting: <u>No Authors ***</u></small>
								<small><u>No Authors ***</u></small>
									% endif
								% endif
							% else:
								<h5>No Title</h5>
							% endif
					</div><!-- End .col-sm-12 -->
				</div><!-- End .row -->
					<% counter += 1 %>
						% endif
					% endfor
				</section>
				</div><!-- end padding -->
				% else:
				<div class="row">
					<div class="col-sm-12 mb0-xs">	
						<p><h5>No Agenda</h5></p>
					</div><!-- End .col-sm-12 -->
				</div><!-- End .row -->
				% endif 
		</div><!-- End .col-sm-12 -->
	</div><!-- End .row -->
	</div>
</div>
	##<script src="/static/js/bootstrap.min.js"></script>

</body>
</html>