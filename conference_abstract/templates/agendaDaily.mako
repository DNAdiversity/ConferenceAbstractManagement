<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<!--[if IE 9]> <html class="ie9"> <![endif]-->
<!--[if !IE]><!--> <html> <!--<![endif]-->
<%
colours = {'Introduction':'',
'Wildlife Forensics & Conservation 1':'#e8f7ef',
'Plants 1 (Overview & Methods)':'#e9d9ac',
'eDNA & Metabarcoding 1 (Freshwater)':'#dff2ec',
'Microbiomes & Mycobiomes':'#F6F4E8',
'Fish Barcode of Life':'#F6F4E8',
'Lepidoptera Biodiversity 1':'#e89d5a',
'eDNA & Metabarcoding 2 (Aquatic)':'#dff2ec',
'Barcode Applications: Terrestrial 1':'#dddeaf',
'Wildlife Forensics & Conservation 2':'#e8f7ef',
'Authentication: Food':'#F6F4E8',
'Marine Biodiversity':'#F6F4E8',
'Lepidoptera Diversity 2 / Terrestrial Biodiversity 1':'#e89d5a',
'African Biomes and Applications':'',
'eDNA & Metabarcoding 3 (Soil) / Wildlife Forensics & Conservation 3':'#e8f7ef',
'eDNA & Metabarcoding 4':'#dff2ec',
'Methodological Advances: Collections':'#F6F4E8',
'Terrestrial Biodiversity 2':'#dae7c4',
'Plenary 3':'',
'Evolution: Genes to Communities':'#d8eceb',
'Ecology: Pollination':'#F6F4E8',
'Authentication: Medicinal Plants 1':'#e5b87d',
'eDNA & Metabarcoding 5':'#dff2ec',
'Barcoding Networks':'#F6F4E8',
'Terrestrial Biodiversity 3':'#dae7c4',
'Methodological Advances 2 (Genomics)':'#E7E3C4',
'Biodiversity Surveys 1':'#F6F4E8',
'Authentication: Medicinal Plants 2':'#e5b87d',
'Evolution: Diversity & Distributions':'#d8eceb',
'Barcode Applications: Aquatic':'#dddeaf',
'Fungal Diversity':'#F6F4E8',
'Planary 4':'',
'eDNA & Metabarcoding 6':'#dff2ec',
'Biodiversity Surveys 2':'#F6F4E8',
'Plants 2 (Taxonomic focus)':'#e9d9ac',
'Evolution: Phylogenetics':'#d8eceb',
'Barcode Applications:  Terrestrial 2':'#dddeaf',
'Freshwater Biodiversity 1':'#E5847D',
'Ecology: Diet & Networks':'#F6F4E8',
'Methodological Advances 3':'#E7E3C4',
'Plants 3':'#e9d9ac',
'Evolution: Community Structure':'#d8eceb',
'eDNA & Metabarcoding 7':'#dff2ec',
'Freshwater Biodiversity 2 / Terrestrial Vertebrates':'#E5847D',
'Lightning Presentation 1':'',
'Lightning Presentation 3':'',
'Lightning Presentation 2':'',
'Closing Plenary':'',}

plenaryDays = {'Day 1 - 09:00':'Day 1','Day 2 - 09:00':'Day 2','Day 3 - 09:00':'Day 3','Day 4 - 09:00':'Day 4 Morning','Day 4 - 15:30':'Day 4 Afternoon'}
days = {'Day 1':'Tuesday, November 21st','Day 2':'Wednesday, November 22nd','Day 3':'Thursday, November 23rd','Day 4':'Friday, November 24th'}

currentDate = ""
currentDateTime = ""
htmlTime = ""
htmlChair = ""
htmlSpeakers = ""
day = "all"
if "day" in request.GET:
	day = int(request.GET.get("day",0))
	if day > 4 or day < 1:
		day = "all"
%>
<head>
	<meta charset="utf-8">
	<title>Conference Abstracts: International Barcode of Life 2017</title>
	<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, minimum-scale=1.0, user-scalable=no">
	<meta name="apple-mobile-web-app-capable" content="yes">
	<meta name="apple-touch-fullscreen" content="yes">
	<meta name="description" content="7th annual DNA">
	<!-- Favicon and Apple Icons -->
	<link rel="icon" type="image/png" href="images/icons/favicon.png">
	<link rel="apple-touch-icon" sizes="57x57" href="images/icons/faviconx57.png">
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
	padding-bottom: 10px;
	padding-top:10px;
	border-bottom: 5px solid #030303;
	padding-left:10px;
	padding-right:10px;
	margin-bottom:5px;
	margin-top:5px;
}
small.presenting{
	font-size:9px;
}

@media print {
	section {page-break-after: always;}
}
ul{
	margin: 0 0 1em 0;
	padding: 0 0 0 1em;
	list-style: none;
}
li {
	position: relative;
	padding-left: 0.01em;
	font-size:smaller;
}
ul li:before{
	content:"\203a";
	position: absolute;
	left:-0.75em;
}
.table td{
	/*word-break: break-all;*/
	
}
</style>
</head>
<body>

<div id="content" role="main">
	<div class="container">
		<div class="row">
			<div class="col-sm-12">
				<h2 class="title-border custom mb40"  style="border-top: 5px solid #030303;padding-top:5px">Plenary Sessions</h2>
				<section>
				<table class="table table-colored table-bordered table-condensed">
			<%
			htmlDays = ""
			htmlSpeakers = ""
			htmlChair = ""
			showFeaturedMessage = False
			%>
			% for agenda in agendas:
				% if "plenary" in agenda["session_id"].lower():
					<%
					parseDate = agenda["date_time"].split("-")
					htmlDays += "<th width='20%'>"+agenda["date_time"]+"</th>"
					htmlChair += "<td>"+agenda["chair"]+"</td>"
					htmlSpeakers += "<td><ul><li>"+"</li><li>".join(agenda["speakers"]).decode("utf-8")+"</li></ul></td>"
					%>
				% endif
			% endfor
					<thead><tr>${htmlDays|n}</tr></thead>
					<tbody>
						##<tr>${htmlChair|n}</tr>
						<tr>${htmlSpeakers|n}</tr>
					</tbody>
				</table>
			<%
				htmlSpeakers = ""
				htmlChair = ""
			%>
				</section>
				<h2 class="title-border custom mb40">Parallel Sessions Agenda</h2>
			% for agenda in agendas:
				<%
				parseDate = agenda["date_time"].split("-")
				goodRow = True
				if "introduction" in agenda["session_name"].lower() or "plenary" in agenda["session_name"].lower():
					goodRow = False
				%>
				% if goodRow == True:
				% if parseDate[0].strip() != currentDate:
					% if currentDateTime != agenda["date_time"] and currentDate != "":
						${htmlTime|n}${htmlChair|n}${htmlSpeakers|n}
						<%
						htmlTime = ""
						htmlChair = ""
						htmlSpeakers = ""
						%>
					% endif
					% if currentDate != "":

				</tbody>
			</table>
			%if showFeaturedMessage == True:
			<h6>** Featured talk</h6> 
			% endif
			</section>
					% endif
					<%
					showFeaturedMessage = False
					currentDate = parseDate[0].strip()
					%>
			<section>
			<h4>${days[parseDate[0].strip()]}: ${parseDate[0]|trim}</h4>
			<table class="table table-colored table-bordered table-condensed">
				<thead>
					<tr bgcolor="">
						<th width="10%"></th>
						<th width="15%">Ndlopfu Room</th> 
						<th width="15%">Goldfields Room</th>
						<th width="15%">Ingwe Room</th>
						<th width="15%">Ndau Room</th>
						<th width="15%">Mhelembe Room</th>
						<th width="15%">Nari Room</th>
					</tr>
				</thead>
				<tbody>
				% endif
				% if currentDateTime != agenda["date_time"]:
					${htmlTime|n}
					${htmlChair|n}
					${htmlSpeakers|n}
					<%
					agendaTime = agenda["date_time"].split("-",1)
					htmlTime = "<tr><td><strong>"+agendaTime[0]+"<br/>"+agendaTime[1]+"</strong></td>"
					htmlChair = "</tr><tr><td>Chair</td>"
					htmlSpeakers = "</tr><tr><td>Speakers</td>"
					currentDateTime = agenda["date_time"]
					%>
				% endif
				<%
				
				if agenda["session_name"] is None:
					htmlTime += "<td></td>"
				else:
					style = " style='background-color:#ebeccc'"
					if agenda["session_name"] in colours:
						if colours[agenda["session_name"]] != "":
							style += ""
							##style = " style='background-color:"+colours[agenda["session_name"]]+"'"
					htmlTime +="<td"+style+">"+agenda["session_name"]+"</td>"
				if agenda["chair"] is None:
					htmlChair += "<td></td>"
				else:
					htmlChair += "<td>"+agenda["chair"]+"</td>"
				if agenda["speakers"] is None:
					htmlSpeakers += "<td></td>"
				elif agenda["type"] == "Talk":
					if "**" in ",".join(agenda["speakers"]).decode("utf-8"):
						showFeaturedMessage = True
					htmlSpeakers += "<td><ul><li>"+"</li><li>".join(agenda["speakers"]).decode("utf-8").replace("**","<b>**</b>")+"</li></ul></td>"
				else:
					##grey out the lighting talk speakers
					htmlSpeakers += "<td style='background-color: #efefef;'>Lightning session</td>"
				%>
				% endif
			% endfor
					${htmlTime|n}
					${htmlChair|n}
					${htmlSpeakers|n}
						</tr>
				</tbody>
			</table>
			%if showFeaturedMessage == True:
			<h6>** Featured talk</h6> 
			% endif
			</section>
		</div><!-- End .col-sm-12 -->
	</div><!-- End .row -->
	</div>
</div>
<!-- 
${day}
-->
</body>
</html>