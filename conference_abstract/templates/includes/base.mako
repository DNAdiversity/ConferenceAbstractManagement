<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<!--[if IE 9]> <html class="ie9"> <![endif]-->
<!--[if !IE]><!--> <html> <!--<![endif]-->
<head>
<%!
import re
def stripHTML(data):
    p = re.compile(r'<.*?>')
    pTitle = ''
    if not data is UNDEFINED:
        pTitle = ' | ' + p.sub('', data)
    return pTitle
%>
	<meta charset="utf-8">
	<title>Conference Abstracts: International Barcode of Life 2017${pageTitle | n,stripHTML}</title>
	<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, minimum-scale=1.0, user-scalable=no">
	<meta name="apple-mobile-web-app-capable" content="yes">
	<meta name="apple-touch-fullscreen" content="yes">
	<meta name="description" content="7th annual DNA">
	<script type="text/javascript" src="https://code.jquery.com/jquery-1.12.1.min.js"></script>
	<!-- Google Fonts -->
	<link href='http://fonts.googleapis.com/css?family=Lato:400,300,700,900,300italic,400italic,700italic' rel='stylesheet' type='text/css'>
	<link href='http://fonts.googleapis.com/css?family=Raleway:400,200,300,500,600,700,800,900' rel='stylesheet' type='text/css'>
	<link href='http://fonts.googleapis.com/css?family=Montserrat:400,700' rel='stylesheet' type='text/css'>
	<link href='http://fonts.googleapis.com/css?family=Open+Sans:400,300italic,400italic,600italic,700italic,600,800,300,700,800italic' rel='stylesheet' type='text/css'>
	<link href='http://fonts.googleapis.com/css?family=Shadows+Into+Light' rel='stylesheet' type='text/css'>
	<!-- Google Fonts -->

	<link rel="stylesheet" href="/static/css/animate.css">
	<link rel="stylesheet" href="/static/css/bootstrap.min.css">
	<link rel="stylesheet" href="/static/css/bootstrap.min.css">
	<link rel="stylesheet" href="/static/css/style.css">
	<link rel="stylesheet" id="color-scheme" href="/static/css/colors/green.css">
	<link rel="stylesheet" href="/static/template/files/css/font-awesome.min.css">
	<!-- Favicon and Apple Icons -->
	<link rel="icon" type="image/png" href="images/icons/favicon.png">
	<link rel="apple-touch-icon" sizes="57x57" href="images/icons/faviconx57.png">
	<link rel="apple-touch-icon" siz
	<!-- Modernizr -->
	<script src="/static/js/modernizr.js"></script>

	<!--- jQuery -->
	<script src="/static/js/jquery.min.js"></script>

	<script>
	(function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
	(i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
	m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
	})(window,document,'script','https://www.google-analytics.com/analytics.js','ga');

	ga('create', 'UA-372370-6', 'auto');
	ga('send', 'pageview');

	</script>
	<!-- Queryloader -->
	##<script src="/static/js/queryloader2.min.js"></script>
	<style>
		#main-navbar-container{
			height:100px;
		}
		#main-navbar-container img {
			height:auto;
		}
		.fixed #main-navbar-container{
			height:inherit;
		}
		.fixed #main-navbar-container img {
			height:55px;
		}
		.text-center .img-responsive {
			margin: 0 auto;
		}
	</style>
	<%block name="header"></%block>
</head>
	${ next.body() }
</html>
