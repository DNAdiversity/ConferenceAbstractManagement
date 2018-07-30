<%inherit file='includes/base.mako' />
<%block name="header">
</%block>
<body>
<%include file="includes/pageHeader.mako"/>
<%include file="includes/contentHeader.mako"/>

	<div class="row">
		<div class="col-sm-12">
			<h2 class="title-border custom mb40">Abstract Not Found</h2>
			<p>We are unable to find the abstract you are looking for.</p>
			
			
			<input type="button" class="btn btn-custom" value="Back to My Abstracts" onclick="location.href='/dashboard'">

		</div><!-- End .col-sm-12 -->

	</div><!-- End .row -->


<%include file="includes/contentFooter.mako"/>
<%include file="includes/pageFooter.mako"/>
<%include file="includes/pageEndScripts.mako"/>
</body>