<%inherit file='includes/base.mako' />
<%!
from datetime import datetime
from time import strftime

release = datetime(2017,10,17,18,00,00)
now = datetime.now()
%>
<%block name="header">
<script type="text/javascript">
	$(document).ready(function(){
		$(".viewButton").on("click",function(){
			var abstractId = $(this).attr("aid");
			$.ajax({
				url:"/abstract/"+abstractId,
				method:"GET",
				dataType: 'text json',
				cache: false
			}).done(function(data){
				if(data["success"] == true){
					$("#abstractTitle").text(data["abstract"]["title"]);
					$("#abstractText").text(data["abstract"]["abstract_text"]);
					$("#categories").text(data["abstract"]["categories"].replace(/{|}|'/g,'').replace(/,/g, ', '));
					var pType = data["abstract"]["abstract_type"];
					if (pType == "Talk"){
						pType = '<i class="fa fa-microphone first-color" title="Talk"></i> ' + pType;
					} else if (pType == "Lightning Talk"){
						pType = '<i class="fa fa-bolt first-color" title="Lightning Talk"></i> ' + pType;
					} else {
						pType = '<i class="fa fa-file-text-o first-color" title="Poster"></i> ' + pType;
					}
					$("#presentationType").html(pType);
					var authorsText = "";
					var sep = ""
					for (var i=0;i<data["authors"].length;i++){
						authorsText += sep + data["authors"][i];
						sep = ", ";
					}
					$("#authors").text(authorsText);
					if (data["abstract"]["review_status"].toLowerCase() == "unsubmitted"){
						$("#submitForReviewButton").removeClass("hidden");
						$("#submitForReviewButton").attr("aid",abstractId);
					} else {
						if (!$("#submitForReviewButton").hasClass("hidden")){
							$("#submitForReviewButton").addClass("hidden");
							$("#submitForReviewButton").attr("aid",0);
						}
					}
					$("#modalAbstract").modal("show");
				} else {
				}
			});

		})
		% if now > release:
		$(".uploadButton").on("click",function(){
			var abstractId = $(this).attr("aid");
			window.location.href="/abstract/"+abstractId+"/attachment";
		});
		% endif
		% if user.is_admin() or user.is_reviewer:
		$(".aScore").each(function(){
			var selector = $(this)
			var abstractId = $(this).attr("aid");
			$.ajax({
				% if user.is_admin():
				url:"/abstract/"+abstractId+"/score/401383401830284018324",
				% else:
				url:"/abstract/"+abstractId+"/score/${user.chairAccessKey}",
				% endif
				method:"GET",
				dataType: 'text json',
				cache: false
			}).done(function(data){
				if(data["success"] == true){
					$(selector).text(data["scores"]);
					% if user.is_admin():
					$(selector).parent().find(".eScore").text(data["editorScores"].replace(",None","").replace("None",""));
					% endif
				}
			});
		});
		% endif
	});//End Document.ready
</script>
<style>
	.rejected{
		color:#fff;
		background-color: #7647a2;
	}
	.assignedForEdit{
		color:#fff;
		background-color:orangered;
	}
</style>
</%block>
<body>
<%include file="includes/pageHeaderPoster.mako"/>
<%include file="includes/contentHeader.mako"/>

	<div class="row">
		<div class="col-sm-12">
			<h2 class="title-border custom mb40">
			
						% if user.is_admin():
			Administration Dashboard<small></small>
						% elif user.is_reviewer():
			Reviewer Dashboard <small>for ${user.fullname}</small>
						% elif user.is_editor():
			Copy Editor Dashboard <small>for ${user.fullname}</small>
						% else :
			Poster Submission Portal<small> Please use this dashboard to retrieve your Poster ID and to submit poster(s).</small>
			## once submissions are open
						% endif
			</h2>
			
			% if len(abstracts) > 0:
			% if user.is_admin():
			<a href="/abstractDownload" class="pull-right"><i class="fa fa-download fa-2x"></i></a>
			% endif
			<table class="table table-striped table-condensed">
				<thead>
					<tr>
						<th></th>
						% if user.is_admin():
						<th>Submitted Abstracts</th>
						% elif user.is_reviewer():
						<th>Abstracts for Review</th>
						% elif user.is_editor():
						<th>Abstracts for Editing</th>
						% else:
						<th>Your Abstracts</th>
						<th>ID</th>
						% endif
						<th colspan="3"></th>
					</tr>
				</thead>
				<tbody>
				
					% for abstract in abstracts:
						<% 
						showRow = True
						# for admin users don't show the unsubmitted rows
						if user.is_admin() and abstract["review_status"].lower() == "unsubmitted":
							showRow = False
						%>
					% if showRow == True:
					<tr>
						<td class="text-center">
							% if abstract["abstract_type"] == "Talk":
							<i class="fa fa-microphone first-color" title="Talk"></i>
							% elif abstract["abstract_type"] == "Lightning Talk":
							<i class="fa fa-bolt first-color" title="Lightning Talk"></i>
							% else:
							<i class="fa fa-file-text-o first-color" title="Poster"></i>
							% endif
						</td>
						<td><strong>${abstract["title"]}
							<% 
							sep = "" 
							%>
							</strong>
							% if int(abstract["id"]) in authors:
							<br/><small>
								% for author in authors[int(abstract["id"])]:
								${sep}${author.decode('utf-8')}
								<% sep = ", "%>
								% endfor
								<br/>
							</small>
							% endif
						</td>
						<td>${"%03d" % abstract["id"]}</td>
						% if user.is_admin() or user.is_reviewer():
						<td></td>
						% endif
						<td> <br/>
						</td>
						<td>
							<!--<input type="button" value="View" aid="${abstract['id']}" class="btn btn-info viewButton"/>-->
							% if abstract["attachment"] is None:
							##Hidden until we are ready to accept the posters
							% if now > release:
							<input type="button" value="Upload Poster" aid="${abstract['id']}" class="btn btn-success uploadButton"/>
							% else:
							<a data-toggle="modal" data-target="#modalSubmissionOpen" class="btn btn-success">Upload Poster</a>
							% endif
							% endif
						</td>
					</tr>
					% endif
					% endfor
				</tbody>
			</table>
			% elif user.is_reviewer() or user.is_admin():
			<p>There are currently no abstracts for you to review</p>
			<div class="mb20"></div><!-- space -->
			% else:
			<p>You have not submitted any abstracts</p>
			% endif
			<h2 class="title-border custom mb40">Poster Guidelines</h2>
			<ul class="list-style list-disc">
				<li>The digitial posters will be displayed on 42 inch screens in <strong>portrait</strong> orientation at HD resolution (1920 x 1080)</li>
				<li>To set the poster orientation and size in PowerPoint, please follow the steps below:
					<ul>1. Go to Design Tab and select Page Setup/Slide Size, and set 'Custom Size'</ul>
					<ul>2. Enter the width and height of the page as: 52 cm wide by 92.7 cm tall. The slide orientation will automatically adjust to portrait based on the page sizes entered.</ul>
				</li>
				<li>With the above settings, abstract text on the poster is recomended to be of font size 18 pts</li>
				<li>With the above settings, Poster content text on is recomended to be of font size 22 pts</li>
				<li>References are recomended to be placed in the footer with a minimum font size of 16 pts</li>
				<li>Place the Poster ID as found in the table above in the top right or bottom right of each poster</li>
				<li>A 50 pixel margin is recommended to ensure that none of the poster content is cut off by screen bezels</li>
				<li>Submit posters as PDF files only</li>
			</ul>
		</div><!-- End .col-sm-12 -->

	</div><!-- End .row -->

<%include file="includes/contentFooter.mako"/>
<%include file="includes/pageFooter.mako"/>
<%include file="includes/pageEndScripts.mako"/>

<div id="modalAbstract" class="modal fade" role="dialog">
	<div class="modal-dialog modal-lg">
		<!-- Modal content-->
		<div class="modal-content">
			<div class="modal-header">
				<button type="button" class="close" data-dismiss="modal">&times;</button>
				<h3 class="modal-title" id="abstractTitle"></h3>
			</div>
			<div class="modal-body scrollPortlet">
				<h5>Preferred Presentation Type</h5>
				<div id="presentationType"></div>
				<div class="mb20"></div><!-- space -->
				<h5>Abstract</h5>
				<div id="abstractText"></div>
				<div class="mb20"></div><!-- space -->
				<h5>Authors</h5>
				<div id="authors"></div>
				<div class="mb20"></div><!-- space -->
				<h5>Assigned Topics</h5>
				<div id="categories"></div>
			</div>
			<div class="modal-footer"><div class="pull-right"><input type="button" value="Submit For Review" id="submitForReviewButton" class="btn btn-custom2 hidden"/><input type="button" data-dismiss="modal" class="btn btn-dark" value="Close"/></div></div>
		</div>
	</div>
</div>

<div id="modalExample" class="modal fade" role="dialog">
	<div class="modal-dialog modal-lg">
		<!-- Modal content-->
		<div class="modal-content">
			<div class="modal-header">
				<button type="button" class="close" data-dismiss="modal">&times;</button>
				<h3 class="modal-title">Example Abstract</h3>
			</div>
			<div class="modal-body scrollPortlet">

				<h5>Title</h5>
				<p>Assessing DNA barcodes as a diagnostic tool for North American reptiles and amphibians in nature and natural history collections</p>
				<div class="mb20"></div><!-- space -->
				<h5>Preferred Presentation Type</h5>
				<p>Talk <i class="fa fa-microphone first-color"></i></p>
				<div class="mb20"></div><!-- space -->
				<h5>Abstract</h5>
				<p>Background: High rates of loss and species discovery have led to the urgent need for more rapid assessments of species diversity and distribution in the herpetofauna, an approach now offered through DNA barcoding. Prior DNA barcoding work on reptiles and amphibians has revealed higher biodiversity counts than previously estimated due to cases of cryptic and undiscovered species in both classes. Despite past research, these taxa are very much in need of comprehensive species-level coverage. <br><br>

Results: This study constructs a reference library of DNA barcodes for North American reptiles and amphibians and assesses their applicability as a technique for species delimitation. This study also examines the correspondence of current species boundaries with the BIN system. Barcodes were obtained from 732 specimens, representing 282 species (44%) of the North American herpetofauna. Mean intraspecific divergences were 1% and 3%, while average congeneric sequence divergences were 16% and 14% in amphibians and reptiles, respectively. BIN assignments corresponded perfectly with current species boundaries in 58% of these species. Barcode sharing was observed in four genera of reptiles, while deep divergences (>2%) were noted in 21% of the species. Using multiple primers and a refined PCR regime, barcode fragments were recovered from 5 of 208 formalin-fixed specimens, demonstrating that formalin collections can expand genetic databases. <br><br>

Significance: This is the first effort to compile a reference library of DNA barcodes that provides species-level identifications for reptiles and amphibians across a broad geographic area. DNA barcodes from North American herpetofauna were used to quickly and effectively flag errors in museum collections, and cases of BIN splits and merges successfully identified taxa belonging to deeply diverged or hybridizing lineages. This study also highlights the merit of further investigation into obtaining genetic material from formalin-fixed tissue and the use of DNA barcodes for biodiversity forensics.
</p>
				<div class="mb20"></div><!-- space -->
				<h5>Authors</h5>
				<p>E. Anne Chambers and Paul D.N. Hebert</p>

			</div>
			<div class="modal-footer"><div class="pull-right"><input type="button" data-dismiss="modal" class="btn btn-dark" value="Close"/></div></div>
		</div>
	</div>
</div>

<div id="modalConfirm" class="modal fade" role="dialog">
	<div class="modal-dialog">
		<!-- Modal content-->
		<div class="modal-content">
			<div class="modal-header">
				<button type="button" class="close" data-dismiss="modal">&times;</button>
				<h3 class="modal-title">WARNING</h3>
			</div>
			<div class="modal-body scrollPortlet">
				Please confirm that the spelling and grammar is correct using a word processor before submitting this abstract.  Changes will not be allowed once submitted for review.
			</div>
			<div class="modal-footer"><div class="pull-right"><input type="button" id="confirmSubmit" class="btn btn-custom2" value="Submit for Review"><input type="button" data-dismiss="modal" class="btn btn-dark" value="Cancel"/></div></div>
		</div>
	</div>
</div>
<div id="modalSubmissionOpen" class="modal fade" role="dialog">
	<div class="modal-dialog">
		<!-- Modal content-->
		<div class="modal-content">
			<div class="modal-header">
				<button type="button" class="close" data-dismiss="modal">&times;</button>
				<h3 class="modal-title">Poster Submissions</h3>
			</div>
			<div class="modal-body scrollPortlet">
				Poster submissions will open October 18th (SAST)
			</div>
			<div class="modal-footer"><div class="pull-right"><input type="button" data-dismiss="modal" class="btn btn-dark" value="OK"/></div></div>
		</div>
	</div>
</div>
	<!--
% if user.is_admin():
 ${authors}
% endif
	-->
</body>