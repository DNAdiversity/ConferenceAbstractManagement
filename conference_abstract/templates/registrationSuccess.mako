<%inherit file='includes/base.mako' />
<%block name="header">
</%block>
<body>
<%include file="includes/pageHeader.mako"/>
<%include file="includes/contentHeader.mako"/>

	<div class="row">
		<div class="col-sm-12">
			<a href="javascript:window.print()" class="hidden-print pull-right"><i class="fa fa-2x fa-print"></i></a>
			<h2 class="title-border custom mb40">Registration Successful</h2>
			% if password is not UNDEFINED:
			<p>Your email to login is: <b>${email}</b></p>
			<p>Your password is: <b>${password}</b></p>
			% endif
			<p>Please record this information as you will require it to submit your abstract(s).  The login details will also be sent via automated email but may be caught by spam filters.
</p>

		</div><!-- End .col-sm-12 -->

	</div><!-- End .row -->


<%include file="includes/contentFooter.mako"/>
<%include file="includes/pageFooter.mako"/>
<%include file="includes/pageEndScripts.mako"/>
</body>