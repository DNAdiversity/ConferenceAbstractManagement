<%inherit file='includes/base.mako' />
<%block name="header">
</%block>
<body>
<%include file="includes/pageHeader.mako"/>
<%include file="includes/contentHeader.mako"/>

	<div class="row">
		<div class="col-sm-12">
			<h2 class="title-border custom mb40">Abstract submitted for review successfully</h2>
			<p>
				Your abstract <strong>${abstract["title"]}</strong> has been successfully submitted for review by conference Scientific Committee and session chairs.  Your preference for a <strong>${abstract["abstract_type"]}</strong> has been included in the package sent for review. <br><br>
Abstracts that were received by March 31st will be reviewed by April 30th, 2017. Abstracts received between April 1st and April 14th will be reviewed as soon as possible. You will be contacted by the scientific committee or session chairs by May 31st with a decision.<br><br>
Please feel free to submit additional abstracts or return to this site to check the status of your abstract.

			</p><br>	
		<input type="button" class="btn btn-custom" value="Back to My Abstracts" onclick="location.href='/dashboard'">

		</div><!-- End .col-sm-12 -->

	</div><!-- End .row -->


<%include file="includes/contentFooter.mako"/>
<%include file="includes/pageFooter.mako"/>
<%include file="includes/pageEndScripts.mako"/>
</body>