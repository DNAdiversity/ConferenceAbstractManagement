<%inherit file='includes/base.mako' />
<%block name="header">
</%block>
<body>
<%include file="includes/pageHeader.mako"/>
<%include file="includes/contentHeader.mako"/>

	<div class="row">
		<div class="col-sm-12">
			<h2 class="title-border custom mb40">${title}</h2>
			<p>${message|n}</p><br/>
			% if showButton is not UNDEFINED:
				% if showButton == "loginPoster":
				For the <b>Poster Submission Portal</b>&nbsp;&nbsp;&nbsp;<a class="btn btn-success btn-sm" href="/loginPoster">Login Here</a>
				% endif
			% endif
		</div><!-- End .col-sm-12 -->

	</div><!-- End .row -->


<%include file="includes/contentFooter.mako"/>
<%include file="includes/pageFooter.mako"/>
<%include file="includes/pageEndScripts.mako"/>
</body>