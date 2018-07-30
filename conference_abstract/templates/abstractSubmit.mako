<%inherit file='includes/base.mako' />
<%block name="header">
<script type="text/javascript">
	$(document).ready(function(){
		$("#submitForReviewButton").on("click",function(){
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
		
		$("#deleteAndStartAgain").on("click",function(){
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
					window.location.href="/dashboard";
				}
			});
		});
	});

</script>
</%block>
<body>
<%include file="includes/pageHeader.mako"/>
<%include file="includes/contentHeader.mako"/>

	<div class="row">
		<div class="col-sm-12">
			<h2 class="title-border custom mb40">Abstract saved successfully</h2>
			<div class="modal-body scrollPortlet">
				<h5>Title</h5>
				<div>${abstract["title"]}</div>
				<div class="mb20"></div><!-- space -->
				<h5>Preferred Presentation Type</h5>
				<div>${abstract["abstract_type"]}</div>
				<div class="mb20"></div><!-- space -->
				<h5>Abstract</h5>
				<div>${abstract["abstract_text"]}</div>
				<div class="mb20"></div><!-- space -->
				<h5>Authors</h5>
				<div>${", ".join(authors)}</div>
				<div class="mb20"></div><!-- space -->
				<h5>Categories</h5>
				<div>${abstract["categories"][2:len(abstract["categories"])-2].replace("','",",")}</div>
			</div>
			
			<div class="alert alert-info">
              <strong>Note:</strong> Please take this opportunity to review your abstract for spelling and grammar issues.  Once submitted for review, this abstract cannot be changed.  This can also be submitted at a later time.
            </div><!-- End .alert-info -->
			
			<input type="button" class="btn btn-custom3" aid="${abstract['id']}" id="submitForReviewButton" value="Submit This Abstract For Review"/> 
			<input type="button" class="btn btn-custom" value="Submit Later" onclick="location.href='/dashboard'">
			<input type="button" class="btn btn-warning" aid="${abstract['id']}" id="deleteAndStartAgain" value="Delete &amp; Start Again" >
		</div><!-- End .col-sm-12 -->

	</div><!-- End .row -->


<%include file="includes/contentFooter.mako"/>
<%include file="includes/pageFooter.mako"/>
<%include file="includes/pageEndScripts.mako"/>
</body>