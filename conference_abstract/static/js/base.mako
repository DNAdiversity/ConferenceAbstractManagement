<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
"http://www.w3.org/TR/html4/loose.dtd">
<html>
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
	<title>mBrave${pageTitle | n,stripHTML}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, minimum-scale=1.0, user-scalable=no">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-touch-fullscreen" content="yes">
    <meta name="description" content="mBrave">
	<script type="text/javascript" src="https://code.jquery.com/jquery-1.12.1.min.js"></script>
	<link href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" rel="stylesheet">
	<script type="text/javascript" src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"></script>
	<script type="text/javascript" src="/static/js/underscore-min.js"></script><!-- for javascript validation -->
	<script type="text/javascript" src="/static/js/backbone.min.js"></script><!-- for javascript validation -->
	<script type="text/javascript" src="/static/js/backbone-validation-min.js"></script><!-- for javascript validation -->
	<script type="text/javascript" src="/static/js/plugins/sweetAlert/sweetalert.min.js"></script><!-- This is the Sweet Alert code -->
	<script type="text/javascript" src="/static/js/plugins/toastr/toastr.min.js"></script>
	<script type="text/javascript" src="http://code.jquery.com/ui/1.12.0/jquery-ui.min.js"></script>
    <script type="text/javascript" src="/static/plugins/Ion.RangeSlider/js/ion-rangeSlider/ion.rangeSlider.min.js"></script>      <!-- Ion Range Slider -->
    <script type="text/javascript" src="/static/date.js"></script>

	<link href="https://maxcdn.bootstrapcdn.com/font-awesome/4.5.0/css/font-awesome.min.css" rel="stylesheet">
	<link type='text/css' href='http://fonts.googleapis.com/css?family=Open+Sans:300,400,400italic,600' rel='stylesheet'>
	<link type="text/css" href="/static/fonts/themify-icons/themify-icons.css" rel="stylesheet">              <!-- Themify Icons -->
	<link rel="stylesheet" href="/static/css/styles.css"><!-- This is the Outline Theme Style -->
	<link rel="stylesheet" href="/static/js/plugins/sweetAlert/sweetalert.css"><!-- This is the Sweet Alert Style -->
	<link rel="stylesheet" href="/static/css/toastr.min.css"><!-- This is the Toastr Style -->
    <link type="text/css" href="/static/plugins/Ion.RangeSlider/css/ion.rangeSlider.css" rel="stylesheet">                    <!-- Ion Range Slider -->
    <link type="text/css" href="/static/plugins/Ion.RangeSlider/css/ion.rangeSlider.skinNice.css" rel="stylesheet">           <!-- Ion Range Slider Default Skin -->
	<style>
		#menuLogin{
			visiblity:hidden;
		}
		#topnav .navbar-brand{
			width:130px !important;
		}
		.req::before{
			content:"* ";
			color:#f00;
		}
        ## setup labels to align right when beside and left when on top
        /* default, mobile-first styles */
        .inputLabel {
            text-align: left;
        }

        /* tablets and upwards */
        @media (min-width: 768px) {
            .inputLabel {
                text-align: right;
            }
        }
        ##TODO: hope that new bootstrap fixes the modal so we can remove the modal-backdrop rule
        .modal-backdrop{
            height:4000px !important;
        }
        ## auto scroll to top
        .scrollToTop {
            bottom: 10px;
            height: 40px;
            opacity: 0;
            position: fixed;
            right: 20px;
            transition: all 0.3s ease-in-out 0s;
            width: 40px;
            z-index: 500;
        }
        .scrollToTop span {
            margin-top: 6px;
        }
        .showScrollTop {
            font-size: 14px;
            opacity: 1;
        }
        ##Debug Class to REMOVE
        .debugScroll{
            overflow: auto;
            word-wrap: normal;
            white-space: pre;
            height:500px;
        }
	</style>
	<!--[if lt IE 10]>
		<script type="text/javascript" src="/static/js/media.match.min.js"></script>
		<script type="text/javascript" src="/static/js/respond.min.js"></script>
		<script type="text/javascript" src="/static/js/placeholder.min.js"></script>
	<![endif]-->
	<script type="text/javascript">
## helpers for forms
        function trimVal(valueToTrim){
            return $.trim(valueToTrim);
        }
        ## Ajax spinner functions
        function showSpinner(parent) {
            $(parent).append(spinner());
        }

        function removeSpinner(parent, timeout) {
            timeout = typeof timeout !== 'undefined' ? timeout : 0;
            setTimeout(function(){
                $(parent).children('#load-spinner').remove();
            }, timeout);
        }

        function failureNotify(parent, data) {
            var msg = "Error loading data. Please refresh the page and contact support@boldsystems.org if issues persist.";
            if (!data) { msg = "No data returned."; }
            $(parent).append(msg);

        }

        function spinner(id) {
            id = typeof id !== 'undefined' ? id : 'load-spinner';
            var s = $('<i>', {class:'fa fa-spinner fa-spin fa-3x fa-fw text-info'});
            return $('<div>', {id:id, class:'text-center m-t-xl'}).append(s);
        }
        ## End ajax spinner functions
		$(window).scroll(function()
		{
			scrollToTopView(); // ScrollToTop button visability toggle
		});
        function scrollToTopView() {
            if($(window).scrollTop() > $(window).height()/3) {
                if(!$('.scrollToTop').hasClass('showScrollTop')) {
                    $('.scrollToTop').addClass('showScrollTop');
                }
            } else {
                $('.scrollToTop').removeClass('showScrollTop');
            }
        };

        // Scroll to target
        function scrollToTarget(D)
        {
            if(D == 1) // Top of page
            {
                D = 0;
            }
            else if(D == 2) // Bottom of page
            {
                D = $(document).height();
            }
            else // Specific Bloc
            {
                D = $(D).offset().top;
                if($('.sticky-nav').length) // Sticky Nav in use
                {
                    D = D-100;
                }
            }

            $('html,body').animate({scrollTop:D}, 'slow');
        }

        ## https://github.com/hongymagic/jQuery.serializeObject
        $.fn.serializeObject = function () {
            "use strict";
            var a = {}, b = function (b, c) {
                var d = a[c.name];
                "undefined" != typeof d && d !== null ? $.isArray(d) ? d.push(c.value) : a[c.name] = [d, c.value] : a[c.name] = c.value
            };
            return $.each(this.serializeArray(), b), a
        };

        ##TODO REMOVE WHEN NOT DEBUGGIN
        function showJSON(title,jsonUrl,obj){
            var dbStr = "";
            title = typeof title != 'undefined' ? ' - ' + title : '';
            if ( obj == 'url'){
                renderDebugJSON(title,jsonUrl,"wait");
                $.ajax({
                    url:        jsonUrl,
                    method:     "GET",
                    dataType:   'text json',
                    cache:      false,
                }).done(function(data){
                    renderDebugJSON(title,jsonUrl,data)
                }).fail(function(data){
                    renderDebugJSON(title,jsonUrl,["Failed to retreive JSON"]);
                });
            } else {
                if (typeof obj != 'string') {
                } else {
                    obj = JSON.parse(obj);
                }
                renderDebugJSON(title,jsonUrl,obj);
            }
        }
        function renderDebugJSON(title,jsonUrl,obj){
            dbSel = "#debugModal";
            dbStr = '<div class="row">';
            dbStr += '<label class="col-xs-1">URL</label>'
            dbStr += '<a class="col-xs-11" href="'+jsonUrl+'">'+jsonUrl+'</a>';
            if (obj == "wait"){
                dbStr += '<div class="text-center m-t-xl"><i class="fa fa-spinner fa-spin fa-3x fa-fw text-info"></i></div>';
            } else {
                dbStr += '<div><pre class="debugScroll">';
                dbStr += JSON.stringify(obj, undefined, 4);
                dbStr += '</pre></div>';
            }
            $(dbSel+"Title").text("Debug Output"+title);
            $(dbSel+"Body").empty();
            $(dbSel+"Body").append(dbStr);
            $(dbSel).modal("show");
        }

        var JSONObjStore = {};
        ## if you don't specify the obj then it will use the url to get it when displaying
        function addJSONObjDebugger(key,selector,title,url,params,obj){
            obj = typeof obj != 'undefined' ? obj : 'url';
            params = typeof params != 'undefined' ? params : '';

            JSONObjStore[key] = {'title':title,'url':url, 'params':params, 'obj':obj};
            debugStr = ' <small><a href="javascript:;" class="debugJSON" key="' + key + '" title="' + title + '"><i class="fa fa-external-link"></i></a></small> ';
            //$(selector).append(debugStr); //DISABLE DEBUG LINKS HERE
            addJSONListeners();
        }

        function addJSONListeners(){
            $(".debugJSON").off();
            $(".debugJSON").on("click",function(){
                JSONObj = JSONObjStore[$(this).attr('key')];
                showJSON(JSONObj['title'],JSONObj['url'],JSONObj['obj']);
            });
        }
        ##TODO: Add back if we want the stick sidebar.  It currently has issue with the minimized sidebar and the secondary menus.
		##$(document).ready(function(){
		##	$("body").addClass("sidebar-scroll");
		##});

	% if user:
		var reauthTime = 300000; //300,000 milisceonds - five minutes
		$(document).ready(function(){
			setTimeout(reauth, reauthTime);
		});

		function reauth() {
			var param = {};
			$.getJSON('/reauth',param, function(data) {
				if(data) {
                    if (data["success"] == true){
                        setTimeout(reauth, reauthTime);
                    } else {
                        showWarning();
                    }
				} else {
                    showWarning();
				}
			});
		}
        function showWarning(){
            toastr.options = {
                "closeButton": true,
                "debug": false,
                "progressBar": false,
                "preventDuplicates": true,
                "positionClass": "toast-top-full-width",
                "onclick": null,
                "showDuration": "400",
                "hideDuration": "0",
                "timeOut": "0",
                "extendedTimeOut": "0",
                "showEasing": "swing",
                "hideEasing": "linear",
                "showMethod": "fadeIn",
                "hideMethod": "fadeOut"
            }
            toastr.warning("Please log in again", 'You\'ve been logged out. Click <a href="/login">here</a> to log back in.');
        }
	% endif
	</script>

	<%block name="header"></%block>
</head>
	${ next.body() }
</html>
