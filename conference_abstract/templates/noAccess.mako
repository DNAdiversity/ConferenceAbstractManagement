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
	<p>Sorry you do not have access to this page</p>
<%include file="includes/contentFooter.mako"/>
<%include file="includes/pageFooter.mako"/>
</body>