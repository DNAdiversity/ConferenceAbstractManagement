<%inherit file='includes/base.mako' />
<%block name="header">
</%block>
<body>
<%include file="includes/pageHeaderPoster.mako"/>
<%include file="includes/contentHeader.mako"/>

	<div class="row">
		<div class="col-sm-12">
			<h2 class="title-border custom mb40">${title}</h2>
			<p>${message|n}</p><br/>
		</div><!-- End .col-sm-12 -->

	</div><!-- End .row -->


<%include file="includes/contentFooter.mako"/>
<%include file="includes/pageFooter.mako"/>
<%include file="includes/pageEndScripts.mako"/>
</body>