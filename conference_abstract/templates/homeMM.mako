<%inherit file='includes/base.mako' />
<%block name="header">
<script src="/static/js/jquery.countTo.js"></script>
</%block>
<%
from datetime import date
from datetime import datetime
today = date.today()

daysTillConference =  (statsAndDates["conference_date"] - today).days
if daysTillConference < 0: daysTillConference = 0

daysTillAbstractsDeadline =  (statsAndDates["abstracts_deadline"] - today).days
if daysTillAbstractsDeadline < 0: daysTillAbstractsDeadline = 0

seatsRemaining = statsAndDates["seats_available"]-statsAndDates["registered_participants"]

seatsAvailable = statsAndDates["seats_available"]

abstractsReceived = statsAndDates["abstracts_received"]

if abstractsReceived<157: abstractsReceived=157

%>
<body>
<%include file="includes/pageHeader.mako"/>
<%include file="includes/contentHeader.mako"/>

	<div class="row">
		<div class="col-sm-12">
			<h2 class="title-border custom mb40">The 7th International Barcode of Life Conference</h2>
			<p>Welcome to the abstract submissions and management system for the <a href="http://dnabarcodes2017.org/">7th International Barcode Of Life Conference</a>, 20-24 November 2017, Kruger National Park, South Africa.</p>
			<h3 class="title-border gray title-bg-line"><span>Conference Details</span></h3>
			<p>The African Centre for DNA Barcoding (ACDB), The International Barcode of Life Project (iBOL), The Department of Environmental Affairs (DEA) and the University of Johannesburg (UJ) will host the 7th International Barcode of Life (iBOL) Conference, 20 – 24 November 2017. This is the first time that this event will be held on the African continent. The venue for the hosting of this prestigious event will be the Nombolo Mdhluli Conference Centre, Skukuza, located within the heart of African wildlife, the Kruger National Park, South Africa.</p>
			<p>Abstract submission opens on 31 January 2017 and now closes on 28 April 2017.  Please create an abstract submission account and login to submit your abstract(s) for oral or poster presentations. Please note - this is not a conference registration!</p>
			% if user is UNDEFINED or user is None:
					<div class="callout bordered">
                    <span class="callout-icon reverse"></span>
                    <div class="callout-wrapper">
                        <div class="callout-right text-left">
                            <h2 class="callout-title">Abstracts submissions are now closed</h2>
                            <p class="callout-desc"></p>
                        </div><!-- End .callout-right -->
						 <div class="callout-right">
                           	<input type="button" class="btn btn-custom" value="Manage Abstracts" onclick="location.href='/login'">
                        </div><!-- End .callout-left -->
                    </div><!-- End .callout-wrapper -->
                </div><!-- End .callout -->
			% else:
			<div class="callout bordered">
                    <span class="callout-icon reverse"></span>
                    <div class="callout-wrapper">
                        <div class="callout-right text-left">
                            <h2 class="callout-title">Abstracts submissions are now closed</h2>
                            <p class="callout-desc"></p>
                        </div><!-- End .callout-right -->
						 <div class="callout-right">
                           	<input type="button" class="btn btn-custom" value="Manage Abstracts" onclick="location.href='/login'">
                        </div><!-- End .callout-left -->
                    </div><!-- End .callout-wrapper -->
                </div><!-- End .callout -->
			% endif
			
			<div class="container">
         
                <div class="row">
                    <div class="col-md-3 col-xs-6 count-container">
                        <span class="count first-color" data-from="${seatsAvailable}" data-to="${seatsRemaining}" data-speed="3000" data-refresh-interval="50">0</span>
                        <h3 class="title-underblock custom">Conference Seats Remaining</h3>
                    </div><!-- End .count-container -->

                    <div class="col-md-3 col-xs-6 count-container">
                        <span class="count first-color" data-from="0" data-to="${abstractsReceived}" data-speed="3000" data-refresh-interval="50">0</span>
                        <h3 class="title-underblock custom">Abstracts Received</h3>
                    </div><!-- End .count-container -->

                    <div class="mb50 visible-sm visible-xs hidden-xss clearfix"></div><!-- space -->

                    <div class="col-md-3 col-xs-6 count-container">
                        <span class="count first-color" data-from="0" data-to="${daysTillAbstractsDeadline}" data-speed="3000" data-refresh-interval="50">0</span>
                        <h3 class="title-underblock custom">Days to Abstracts Deadline</h3>
                    </div><!-- End .count-container -->

                    <div class="col-md-3 col-xs-6 count-container">
                        <span class="count first-color" data-from="0" data-to="${daysTillConference}" data-speed="3000" data-refresh-interval="50">0</span>
                        <h3 class="title-underblock custom">Days to Conference</h3>
                    </div><!-- End .count-container -->
                
				</div><!-- End .row -->
				
            </div><!-- End .container -->		
		
		</div><!-- End .col-sm-12 -->

	</div><!-- End .row -->
<!--<h3 class="title-border gray title-bg-line"><span>Conference Timeline - 2017</span></h3><br/>-->


<h3>Conference Timeline</h3>

<img src="../static/images/timeline_april28.png" width="1200" class="img-responsive" alt=""/>

<!--
<ul class="list-style list-disc">
<li>January 31, 2017 - Abstract Submissions Open</li>
<li>March 31, 2017 - Abstract Submissions Deadline</li>
<li>April 30, 2017 - Abstract Decisions Notification</li>
<li>May 31, 2017 - Early-Bird Registration Deadline</li>
<li>October 31, 2017 - Online Registration Deadline</li>
<li>November 20-24, 2017 - Conference</li>
</ul>-->


<%include file="includes/contentFooter.mako"/>

<%include file="includes/pageFooter.mako"/>
<%include file="includes/pageEndScripts.mako"/>
</body>