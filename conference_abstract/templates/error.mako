<%inherit file='includes/base.mako' />
<%block name="header">
<style>
	#trigger-sidebar{
		visibility:hidden;
	}
</style>
</%block>
<body>
<%include file="includes/pageHeader.mako"/>
<div id="wrapper">
	<div id="layout-static">
<%include file="includes/contentHeader.mako"/>

		<div class="row">
			<div class="col-sm-12">
				<h2 class="title-border custom mb40">Error</h2>
				<p>Unable to perform action. Please try again later or contact support if you need immediate assistance.</p>
			</div>
		</div>
	
<%include file="includes/contentFooter.mako"/>
<%include file="includes/pageFooter.mako"/>
</body>