<%inherit file='includes/base.mako' />
<%!
import datetime
from time import strftime
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
		% if user.is_admin() or user.is_reviewer:
		$(".reviewButton").on("click",function(){
			var abstractId = $(this).attr("aid");
			window.location.href="/abstractReview/"+abstractId;
		});
		% endif
		$("#submitForReviewButton").on("click",function(){
			var abstractId = $(this).attr("aid");
			$("#confirmSubmit").attr("aid",abstractId);
			$("#modalConfirm").modal("show");
		});

		$(".submitForReviewButton").on("click",function(){
			var abstractId = $(this).attr("aid");
			$("#confirmSubmit").attr("aid",abstractId);
			$("#modalConfirm").modal("show");
		});
		$("#confirmSubmit").on("click",function(){
			var abstractId = $(this).attr("aid");
			$.ajax({
				url:"/abstract/"+abstractId+"/update",
				method:"POST",
				dataType: 'text json',
				cache: false
			}).done(function(data){
				if(data["success"] == true){
					/*
					## reload the page so it refreshes the row data
					*/
					window.location.href="/abstractSuccess/"+abstractId;
				}
			});
		});
		$(".editButton").on("click",function(ev){
			ev.preventDefault()
			var abstractId = $(this).attr("aid");
			window.location.href="/abstract/"+abstractId+"/edit";
		});
		$(".removeButton").on("click",function(ev){
			ev.preventDefault()
			var abstractId = $(this).attr("aid");
			$("#confirmDelete").attr("aid",abstractId);
			$("#modalDelete").modal("show");
		});
		$("#confirmDelete").on("click",function(){
			var abstractId = $(this).attr("aid");
			$.ajax({
				url:"/abstract/"+abstractId+"/delete",
				method:"POST",
				dataType: 'text json',
				cache: false
			}).done(function(data){
				if(data["success"] == true){
					/*
					## reload the page so it refreshes the row data
					*/
					window.location.href=window.location.href;
				}
			});
		});
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
				}
			});
		});
		% endif
	});//End Document.ready
</script>
</%block>
<body>
<%include file="includes/pageHeader.mako"/>
<%include file="includes/contentHeader.mako"/>

	<div class="row">
		<div class="col-sm-12">
			<h2 class="title-border custom mb40">
			
						% if user.is_admin():
			Administration Dashboard<small></small>
						% elif user.is_reviewer():
			Reviewer Dashboard <small>for ${user.fullname}</small>
						% else :
			Abstract Management<small> You can submit 1 or more abstract(s) for poster, oral or lightning presentations</small>
						% endif
			</h2>
			
			% if len(abstracts) < 5:
			## What do we do about reviewers are they allowed to submit? Currenlty they could create login to do this
			% if not user.is_admin() and not user.is_reviewer():
			<div class="callout bordered">
				<span class="callout-icon reverse"></span>
				<div class="callout-wrapper">
					
					<div class="callout-center text-center">
						<h2 class="callout-title">Abstract Submission is now closed</h2>
						<p class="callout-desc"></p>
					</div><!-- End .callout-right -->
				</div><!-- End .callout-wrapper -->
			</div><!-- End .callout -->
			% endif
			
			<!--<input type="button" class="btn btn-custom" value="Submit New Abstract" onclick="location.href='/abstractNew'"><br/><br/>-->
			% endif
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
						% else:
						<th>Your Abstracts</th>
						% endif
						% if user.is_admin() or user.is_reviewer():
						<th>Submitter</th>
						% endif
						<th>Date/Status</th>
						% if user.is_admin() or user.is_reviewer():
						<th>Score</th>
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
								${sep}${author}
								<% sep = ", "%>
								% endfor
								<br/>
								<i>${abstract["categories"][2:len(abstract["categories"])-2].replace("','",", ")}</i>
							</small>
							% endif
						</td>
						% if user.is_admin() or user.is_reviewer():
						<td>${abstract["submitter_name"]}</td>
						% endif
						<td>${abstract["modification_date"].strftime('%Y/%m/%d')} <br/>
						% if user.is_admin():
						<span class="highlight 
							% if abstract['review_status'].lower() == 'submitted': 
							third-color
							% elif abstract['review_status'].lower() == 'assigned':
							% else:
							first-color
							% endif
							"><small>${abstract["review_status"].upper()}</small></span>
						% elif user.is_reviewer():
						<span class="highlight 
							% if abstract['review_status'].lower() == 'assigned': 
							third-color
							% else:
							first-color
							% endif
							"><small>${abstract["review_status"].upper()}</small></span>
						% else:
						<span class="highlight 
							% if abstract['review_status'].lower() == 'unsubmitted': 
							third-color
							% else:
							first-color
							% endif
							"><small>${abstract["review_status"].upper()}</small></span>						
						% endif
						</td>
						% if user.is_admin() or user.is_reviewer():
							% if abstract['review_status'] in ["REVIEWED","ASSIGNED"]:
								<td class="aScore" aid="${abstract["id"]}"></td>
							% else:
								<td></td>
							% endif
						% endif
						% if user.is_admin():
						<td>
							##<select class="reviewer" aid="${abstract['id']}"></select>
							<input type="button" value="Assign/Review" aid="${abstract['id']}" class="btn btn-info btn-sm reviewButton"/>
						</td>
						% elif user.is_reviewer():
						<td>
							##<select class="reviewer" aid="${abstract['id']}"></select>
							<input type="button" value="Review" aid="${abstract['id']}" class="btn btn-danger btn-sm reviewButton"/>
						</td>
						% else:
						<td><input type="button" value="View" aid="${abstract['id']}" class="btn btn-info viewButton"/></td>
							% if abstract['review_status'].lower() == 'unsubmitted':
						<td>
							<input type="button" value="Submit For Review" aid="${abstract['id']}" class="btn btn-info submitForReviewButton"/>
						</td>
						<td>
							<a href="" aid="${abstract['id']}" class="btn btn-default btn-border editButton"><i class='fa fa-pencil'></i></a>
							<a href="" aid="${abstract['id']}" class="btn btn-default btn-border removeButton"><i class='fa fa-trash'></i></a>
						</td>
							% else:
						<td colspan="2"></td>
							% endif
						% endif
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
			<h2 class="title-border custom mb40">Abstract Guidelines</h2>
			
			<ul class="list-style list-disc">
			<li>Abstracts must be submitted before April 28, 2017 through this online submission system.</li>
			<li>Submitted abstracts may not exceed 300 words (excluding title, author names and affiliations).</li>
			<li>For works presenting novel data or analyses, three subsections must be used, each followed by a colon - <strong>Background</strong>, <strong>Results</strong>, and <strong>Significance</strong>. Other types of works (e.g. reviews, conceptual advances) may use an alternative structure if suitable.</li>
			<li>Abstract should be written in plain English.</li>
			<li>References should not be cited in the abstract unless they are absolutely essential, in which case full bibliographic information must be provided.</li>
			
			<li>Submitters should select up to 3 session topics that most closely correspond to the research to be presented.</li>
			<li>Abstracts that were received by March 31st will be reviewed by April 30th, 2017. Abstracts received between April 1st and April 28th will be reviewed as soon as possible. You will be contacted by the scientific committee or session chairs by May 31st with a decision.</li>
			<li>All accepted abstracts from both the oral and poster presentation sessions will be published in a special issue of the journal Genome.</li>
			<li>Prize winners, together with other outstanding contributors to the poster and parallel sessions, will be invited to submit their work as full journal articles for a special conference issue.</li>
			<li>A lightning talk is a 5 minute presentation with slides that will be presented during sessions</li>
			</ul><br>
			 <button class="btn btn-custom" data-toggle="modal" data-target="#modalExample">View Example Abstract</button>

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
				<h5>Selected Session Topics</h5>
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
<div id="modalDelete" class="modal fade" role="dialog">
	<div class="modal-dialog">
		<!-- Modal content-->
		<div class="modal-content">
			<div class="modal-header">
				<button type="button" class="close" data-dismiss="modal">&times;</button>
				<h3 class="modal-title">WARNING</h3>
			</div>
			<div class="modal-body scrollPortlet">
				Are you sure you want to delete this abstract? Once deleted it will no longer be available for recovery.
			</div>
			<div class="modal-footer"><div class="pull-right"><input type="button" id="confirmDelete" class="btn btn-custom2" value="Delete"><input type="button" data-dismiss="modal" class="btn btn-dark" value="Cancel"/></div></div>
		</div>
	</div>
</div>
	
</body>