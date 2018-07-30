<%inherit file='includes/base.mako' />
<%
fullCountryNameArray = {
"AF":"Afghanistan",
"AL":"Albania",
"DZ":"Algeria",
"AS":"American Samoa",
"AD":"Andorra",
"AO":"Angola",
"AI":"Anguilla",
"AQ":"Antarctica",
"AG":"Antigua and Barbuda",
"AR":"Argentina",
"AM":"Armenia",
"AW":"Aruba",
"AU":"Australia",
"AT":"Austria",
"AZ":"Azerbaijan",
"BS":"Bahamas",
"BH":"Bahrain",
"BD":"Bangladesh",
"BB":"Barbados",
"BY":"Belarus",
"BE":"Belgium",
"BZ":"Belize",
"BJ":"Benin",
"BM":"Bermuda",
"BT":"Bhutan",
"BO":"Bolivia, Plurinational State of",
"BQ":"Bonaire, Sint Eustatius and Saba",
"BA":"Bosnia and Herzegovina",
"BW":"Botswana",
"BV":"Bouvet Island",
"BR":"Brazil",
"IO":"British Indian Ocean Territory",
"BN":"Brunei Darussalam",
"BG":"Bulgaria",
"BF":"Burkina Faso",
"BI":"Burundi",
"KH":"Cambodia",
"CM":"Cameroon",
"CA":"Canada",
"CV":"Cape Verde",
"KY":"Cayman Islands",
"CF":"Central African Republic",
"TD":"Chad",
"CL":"Chile",
"CN":"China",
"CX":"Christmas Island",
"CC":"Cocos (Keeling) Islands",
"CO":"Colombia",
"KM":"Comoros",
"CG":"Congo",
"CD":"Congo, the Democratic Republic of the",
"CK":"Cook Islands",
"CR":"Costa Rica",
"CI":"Cote d'Ivoire",
"HR":"Croatia",
"CU":"Cuba",
"CW":"Curaçao",
"CY":"Cyprus",
"CZ":"Czech Republic",
"DK":"Denmark",
"DJ":"Djibouti",
"DM":"Dominica",
"DO":"Dominican Republic",
"EC":"Ecuador",
"EG":"Egypt",
"SV":"El Salvador",
"GQ":"Equatorial Guinea",
"ER":"Eritrea",
"EE":"Estonia",
"ET":"Ethiopia",
"FK":"Falkland Islands (Malvinas)",
"FO":"Faroe Islands",
"FJ":"Fiji",
"FI":"Finland",
"FR":"France",
"GF":"French Guiana",
"PF":"French Polynesia",
"TF":"French Southern Territories",
"GA":"Gabon",
"GM":"Gambia",
"GE":"Georgia",
"DE":"Germany",
"GH":"Ghana",
"GI":"Gibraltar",
"GR":"Greece",
"GL":"Greenland",
"GD":"Grenada",
"GP":"Guadeloupe",
"GU":"Guam",
"GT":"Guatemala",
"GG":"Guernsey",
"GN":"Guinea",
"GW":"Guinea-Bissau",
"GY":"Guyana",
"HT":"Haiti",
"HM":"Heard Island and McDonald Islands",
"VA":"Holy See (Vatican City State)",
"HN":"Honduras",
"HK":"Hong Kong",
"HU":"Hungary",
"IS":"Iceland",
"IN":"India",
"ID":"Indonesia",
"IR":"Iran, Islamic Republic of",
"IQ":"Iraq",
"IE":"Ireland",
"IM":"Isle of Man",
"IL":"Israel",
"IT":"Italy",
"JM":"Jamaica",
"JP":"Japan",
"JE":"Jersey",
"JO":"Jordan",
"KZ":"Kazakhstan",
"KE":"Kenya",
"KI":"Kiribati",
"KP":"Korea, Democratic People's Republic of",
"KR":"Korea, Republic of",
"KW":"Kuwait",
"KG":"Kyrgyzstan",
"LA":"Lao People's Democratic Republic",
"LV":"Latvia",
"LB":"Lebanon",
"LS":"Lesotho",
"LR":"Liberia",
"LY":"Libya",
"LI":"Liechtenstein",
"LT":"Lithuania",
"LU":"Luxembourg",
"MO":"Macao",
"MK":"Macedonia, the former Yugoslav Republic of",
"MG":"Madagascar",
"MW":"Malawi",
"MY":"Malaysia",
"MV":"Maldives",
"ML":"Mali",
"MT":"Malta",
"MH":"Marshall Islands",
"MQ":"Martinique",
"MR":"Mauritania",
"MU":"Mauritius",
"YT":"Mayotte",
"MX":"Mexico",
"FM":"Micronesia, Federated States of",
"MD":"Moldova, Republic of",
"MC":"Monaco",
"MN":"Mongolia",
"ME":"Montenegro",
"MS":"Montserrat",
"MA":"Morocco",
"MZ":"Mozambique",
"MM":"Myanmar",
"NA":"Namibia",
"NR":"Nauru",
"NP":"Nepal",
"NL":"Netherlands",
"NC":"New Caledonia",
"NZ":"New Zealand",
"NI":"Nicaragua",
"NE":"Niger",
"NG":"Nigeria",
"NU":"Niue",
"NF":"Norfolk Island",
"MP":"Northern Mariana Islands",
"NO":"Norway",
"OM":"Oman",
"PK":"Pakistan",
"PW":"Palau",
"PS":"Palestinian Territory, Occupied",
"PA":"Panama",
"PG":"Papua New Guinea",
"PY":"Paraguay",
"PE":"Peru",
"PH":"Philippines",
"PN":"Pitcairn",
"PL":"Poland",
"PT":"Portugal",
"PR":"Puerto Rico",
"QA":"Qatar",
"RE":"Réunion",
"RO":"Romania",
"RU":"Russian Federation",
"RW":"Rwanda",
"BL":"Saint Barthélemy",
"SH":"Saint Helena, Ascension and Tristan da Cunha",
"KN":"Saint Kitts and Nevis",
"LC":"Saint Lucia",
"MF":"Saint Martin (French part)",
"PM":"Saint Pierre and Miquelon",
"VC":"Saint Vincent and the Grenadines",
"WS":"Samoa",
"SM":"San Marino",
"ST":"Sao Tome and Principe",
"SA":"Saudi Arabia",
"SN":"Senegal",
"RS":"Serbia",
"SC":"Seychelles",
"SL":"Sierra Leone",
"SG":"Singapore",
"SX":"Sint Maarten (Dutch part)",
"SK":"Slovakia",
"SI":"Slovenia",
"SB":"Solomon Islands",
"SO":"Somalia",
"ZA":"South Africa",
"GS":"South Georgia and the South Sandwich Islands",
"SS":"South Sudan",
"ES":"Spain",
"LK":"Sri Lanka",
"SD":"Sudan",
"SR":"Suriname",
"SJ":"Svalbard and Jan Mayen",
"SZ":"Swaziland",
"SE":"Sweden",
"CH":"Switzerland",
"SY":"Syrian Arab Republic",
"TW":"Taiwan, Province of China",
"TJ":"Tajikistan",
"TZ":"Tanzania, United Republic of",
"TH":"Thailand",
"TL":"Timor-Leste",
"TG":"Togo",
"TK":"Tokelau",
"TO":"Tonga",
"TT":"Trinidad and Tobago",
"TN":"Tunisia",
"TR":"Turkey",
"TM":"Turkmenistan",
"TC":"Turks and Caicos Islands",
"TV":"Tuvalu",
"UG":"Uganda",
"UA":"Ukraine",
"AE":"United Arab Emirates",
"GB":"United Kingdom",
"US":"United States",
"UM":"United States Minor Outlying Islands",
"UY":"Uruguay",
"UZ":"Uzbekistan",
"VU":"Vanuatu",
"VE":"Venezuela, Bolivarian Republic of",
"VN":"Viet Nam",
"VG":"Virgin Islands, British",
"VI":"Virgin Islands, U.S.",
"WF":"Wallis and Futuna",
"EH":"Western Sahara",
"YE":"Yemen",
"ZM":"Zambia",
"ZW":"Zimbabwe"
}

%>
<%block name="header">
<script type="text/javascript">
	$(document).ready(function(){
		$("#submitForReviewButton").on("click",function(){
			var abstractId = $(this).attr("aid");
			$.ajax({
				url:"/abstract/"+abstractId+"/update",
				method:"POST",
				dataType: 'text json',
				cache: false
			}).done(function(data){
				if(data["success"] == true){
					/*
					## reload the page so it refreshes the row data
					*/
					window.location.href="/abstractSuccess/"+abstractId;
				}
			});
		});
		$(".reviewer").each(function(){
			var selector = $(this);
			var abstractId = $(this).attr("aid");
			$.ajax({
				url:"/abstract/"+abstractId+"/chair",
				method:"GET",
				dataType: 'text json',
				cache: false
			}).done(function(data){
				if(data["success"] == true){
					if ($(selector).attr("origRid") == 0){
						var optionsHTML = "<option value='0'>Select a Reviewer</option>";
					} else {
						var optionsHTML = "";
					}
					
					if (data["topicChairs"].length>0){
						optionsHTML += "<optgroup label='Recommended Reviewers (based on topic)'>"
						for (var i=0;i<data["topicChairs"].length;i++){
							optionsHTML += "<option value='"+data["topicChairs"][i]["id"]+"' remail='"+data["topicChairs"][i]["email"]+"'>"+data["topicChairs"][i]["fullname"]+" ("+ data["topicChairs"][i]["topics"] +")</option>";
						}
						optionsHTML += "</optgroup>";
					}
					if (data["categoryChairs"].length>0){
						optionsHTML += "<optgroup label='Alternate Reviewers (Category-based)'>"
						for (var i=0;i<data["categoryChairs"].length;i++){
							optionsHTML += "<option value='"+data["categoryChairs"][i]["id"]+"' remail='"+data["categoryChairs"][i]["email"]+"'>"+data["categoryChairs"][i]["fullname"]+" ("+ data["categoryChairs"][i]["categories"] +")</option>";
						}
						optionsHTML += "</optgroup>";
					}
					if ($(selector).attr("origRid") == 0){
						
					} else {
						optionsHTML += "<option value='-1'>--No Reviewer</option>";
					}
					
					$(selector).html(optionsHTML);
					$(selector).val($(selector).attr("origRid"))
				}
			});
		});
		$(".assignReviewer").on("click",function(){
			var selectedReviewer = $(this).parent().parent().find("#selectedReviewer").val()
			var originalReviewer = $(this).parent().parent().find("#selectedReviewer").attr("origRid");
			var reviewerEmail = "";
			var reviewerName = "";
			if (selectedReviewer>0 && selectedReviewer != originalReviewer){
				reviewerEmail = $(this).parent().parent().find("#selectedReviewer option:selected").attr("remail")
				var duplicateReviewer = false;
				$(".reviewer").each(function(){
					if ($(this).attr("origRid") != originalReviewer && $(this).val() == selectedReviewer){
						duplicateReviewer = true;
					}
				});
				if ( duplicateReviewer == false ){
					$("#reviewerName").text($(this).parent().parent().find("#selectedReviewer option:selected").text());
					$("#reviewerName2").text($("#reviewerName").text());
					$("#reviewerEmail").html('<a href="mailto:'+reviewerEmail+'">'+reviewerEmail+'</a>');
					$("#confirmReviewer").attr("rid",selectedReviewer);
					$("#confirmReviewer").attr("origRid",originalReviewer);
					$("#modalConfirm").modal("show");
				} else {
					alert("You already have this reviewer assigned");
				}
			} else if (selectedReviewer == -1){
				$("#confirmReviewer").attr("rid",originalReviewer)
				$(this).parent().parent().find("#selectedReviewer option").each(function(){
					if ($(this).val()==originalReviewer){
						reviewerEmail = $(this).attr("remail");
						reviewerName = $(this).text();
					}
				});
				$("#reviewerRemovalName").text(reviewerName);
				$("#reviewerRemovalEmail").html('<a href="mailto:'+reviewerEmail+'">'+reviewerEmail+'</a>');
				$("#confirmReviewerRemoval").attr("rid",originalReviewer);
				$("#modalConfirmRemoval").modal("show");
			}
		});
		$("#confirmReviewer").on("click",function(){
			var abstractId = $(this).attr("aid");
			var params = {"reviewerId":$(this).attr("origRid")};
			var reviewerId = $(this).attr("rid");
			if ($(this).attr("origRid") == 0){
				console.log("don't unassign as there is no one")
				params = {"reviewerId":$(this).attr("rid")};
				$.ajax({
					url:"/abstract/"+abstractId+"/assign",
					method:"POST",
					data:params,
					dataType: 'text json',
					cache: false
				}).done(function(data){
					if(data["success"] == true){
						window.location.href="/dashboard";
					}
				});
			} else {
				$.ajax({
					url:"/abstract/"+abstractId+"/unassign",
					method:"POST",
					data:params,
					dataType: 'text json',
					cache: false
				}).done(function(data){
					if(data["success"] == true){
						params = {"reviewerId":reviewerId};
						$.ajax({
							url:"/abstract/"+abstractId+"/assign",
							method:"POST",
							data:params,
							dataType: 'text json',
							cache: false
						}).done(function(data){
							if(data["success"] == true){
								window.location.href="/dashboard";
							}
						});
					}
				});
			}
		});
		$("#confirmReviewerRemoval").on("click",function(){
			var abstractId = $(this).attr("aid");
			var params = {"reviewerId":$(this).attr("rid")};
			$.ajax({
				url:"/abstract/"+abstractId+"/unassign",
				method:"POST",
				data:params,
				dataType: 'text json',
				cache: false
			}).done(function(data){
				if(data["success"] == true){
					window.location.href="/dashboard";
				}
			});
		});
		% if user.is_admin():
		$(".editor").each(function(){
			var selector = $(this);
			var abstractId = $(this).attr("aid");
			$.ajax({
				url:"/abstract/"+abstractId+"/copyeditor",
				method:"GET",
				dataType: 'text json',
				cache: false
			}).done(function(data){
				if(data["success"] == true){
					if ($(selector).attr("origEid") == 0){
						var optionsHTML = "<option value='0'>Select an Editor</option>";
					} else {
						var optionsHTML = "";
					}
					
					if (data["copyEditors"].length>0){
						for (var i=0;i<data["copyEditors"].length;i++){
							optionsHTML += "<option value='"+data["copyEditors"][i]["id"]+"' eemail='"+data["copyEditors"][i]["email"]+"'>"+data["copyEditors"][i]["fullname"]+"</option>";
						}
					}
					if ($(selector).attr("origRid") == 0){
						
					} else {
						optionsHTML += "<option value='-1'>--No Editor</option>";
					}
					
					$(selector).html(optionsHTML);
					$(selector).val($(selector).attr("origEid"))
				}
			});
		});

		$(".assignEditor").on("click",function(){
			var selectedEditor = $(this).parent().parent().find("#selectedEditor").val()
			var originalEditor = $(this).parent().parent().find("#selectedEditor").attr("origEid");
			var editorEmail = "";
			var editorName = "";
			if (selectedEditor>0 && selectedEditor != originalEditor){
				editorEmail = $(this).parent().parent().find("#selectedEditor option:selected").attr("eemail")
				var duplicateReviewer = false;
				$(".editor").each(function(){
					if ($(this).attr("origEid") != originalEditor && $(this).val() == selectedReviewer){
						duplicateReviewer = true;
					}
				});
				if ( duplicateReviewer == false ){
					$("#editorName").text($(this).parent().parent().find("#selectedEditor option:selected").text());
					$("#editorName2").text($("#editorName").text());
					$("#editorEmail").html('<a href="mailto:'+editorEmail+'">'+editorEmail+'</a>');
					$("#confirmEditor").attr("eid",selectedEditor);
					$("#confirmEditor").attr("origEid",originalEditor);
					$("#modalConfirmEditor").modal("show");
				} else {
					alert("You already have this reviewer assigned");
				}
			} else if (selectedEditor == -1){
				$("#confirmEditor").attr("eid",originalEditor)
				$(this).parent().parent().find("#selectedEditor option").each(function(){
					if ($(this).val()==originalEditor){
						editorEmail = $(this).attr("eemail");
						editorName = $(this).text();
					}
				});
				$("#editorRemovalName").text(editorName);
				$("#editorRemovalEmail").html('<a href="mailto:'+editorEmail+'">'+editorEmail+'</a>');
				$("#confirmEditorRemoval").attr("eid",originalEditor);
				$("#modalConfirmEditorRemoval").modal("show");
			}
		});
		$("#confirmEditor").on("click",function(){
			var abstractId = $(this).attr("aid");
			var params = {"copyEditorId":$(this).attr("origEid")};
			var copyEditorId = $(this).attr("eid");
			if (parseInt($(this).attr("origEid")) == 0){
				console.log("don't unassign as there is no one")
				params = {"copyEditorId":$(this).attr("eid")};
				$.ajax({
					url:"/abstract/"+abstractId+"/assignEditor",
					method:"POST",
					data:params,
					dataType: 'text json',
					cache: false
				}).done(function(data){
					if(data["success"] == true){
						window.location.href="/dashboard";
					}
				});
			} else {
				$.ajax({
					url:"/abstract/"+abstractId+"/unassignEditor",
					method:"POST",
					data:params,
					dataType: 'text json',
					cache: false
				}).done(function(data){
					if(data["success"] == true){
						params = {"copyEditorId":copyEditorId};
						$.ajax({
							url:"/abstract/"+abstractId+"/assignEditor",
							method:"POST",
							data:params,
							dataType: 'text json',
							cache: false
						}).done(function(data){
							if(data["success"] == true){
								window.location.href="/dashboard";
							}
						});
					}
				});
			}
		});
		$("#confirmEditorRemoval").on("click",function(){
			var abstractId = $(this).attr("aid");
			var params = {"copyEditorId":$(this).attr("eid")};
			$.ajax({
				url:"/abstract/"+abstractId+"/unassignEditor",
				method:"POST",
				data:params,
				dataType: 'text json',
				cache: false
			}).done(function(data){
				if(data["success"] == true){
					window.location.href="/dashboard";
				}
			});
		});
		% endif
		% if user.is_reviewer() and user.chairId in reviewers:

		$.ajax({
			url:"/abstract/${abstract["id"]}/score/${user.chairAccessKey}",
			method:"GET",
			dataType: 'text json',
			cache: false
		}).done(function(data){
			if(data["success"] == true){
				$("#score").val(data["score"]);
				$("#suggestedTopic").val(data["suggestedTopic"]);
			}
		});

		$("#saveScoreButton").on("click",function(){
			var abstractId = $(this).attr("aid");
			if ($("#score").val() != ""){
				$("#saveScore").text($("#score").val());
				if ($("#suggestedTopic").val() != ""){
					$("#saveTopic").text($("#suggestedTopic option:selected").text());				
					$("#suggestedTopicSelected").show();
				} else {
					$("#suggestedTopicSelected").hide();
				}
				$("#modalConfirmSaveScore").modal("show");
			} else {
				alert("Please select a score to save");
			}
		});
		$("#confirmSaveScore").on("click",function(){
			var abstractId = $(this).attr("aid");
			params = {"score":$("#score").val(),"suggestedTopic":$("#suggestedTopic").val(),"notes":$("#reviewerNotes").val()}
			//console.log(params)
			$.ajax({
				url:"/abstract/"+abstractId+"/score/${user.chairAccessKey}",
				method:"POST",
				data:params,
				dataType: 'text json',
				cache: false
			}).done(function(data){
				if(data["success"] == true){
					window.location.href="/dashboard";
				}
			});
		});
		% endif
	});
</script>
</%block>
<%!
import unicodedata
%>
<body>
<%include file="includes/pageHeader.mako"/>
<%include file="includes/contentHeader.mako"/>

	<div class="row">
		<div class="col-sm-12">
			<h2 class="title-border custom mb40">Abstract Under Review</h2>
			<p>Please assign a reviewer or assign a score to this abstract</p>
			<div class="alert alert-info">
				<strong>STATUS:</strong> ${abstract["review_status"]}
			</div>
				% if len(abstractHistory) > 0:
				<div style="position:relative;border-bottom:1px solid #000; padding:10px 0px;margin-bottom:10px">
					<h4>Abstract Review History</h4>
					<div class="container">
						<div class="row">
							<div class="col-xs-12 table-responsive">
								<table class="table table-condensed table-striped">
									<thead>
										<tr>
											<th>Review Date</th>
											<th>Reviewer</th>
											<th>Score</th>
											<th>Suggested Topic</th>
											<th>Notes</th>
										</tr>
									</thead>
									<tbody>
										% for history in abstractHistory:
										<tr>
											<td>${history["scoreDate"]}</td>
											<td>${history["reviewerFullname"]}</td>
											<td>${history["score"]}</td>
											<td>${history["topic"]}</td>
											<td>${history["notes"]}</td>
										</tr>
										% endfor
									</tbody>
								</table>
							</div>
						</div>
					</div>
				</div>
				% endif
			<div>
				<h5>Title</h5>
				<div>${abstract["title"].decode('utf-8')}</div>
				<div class="mb20"></div><!-- space -->
				<h5>Preferred Presentation Type</h5>
				<div>
					% if abstract["abstract_type"] == "Talk":
					<i class="fa fa-microphone first-color" title="Talk"></i>
					% elif abstract["abstract_type"] == "Lightning Talk":
					<i class="fa fa-bolt first-color" title="Lightning Talk"></i>
					% else:
					<i class="fa fa-file-text-o first-color" title="Poster"></i>
					% endif
					 ${abstract["abstract_type"]}</div>
				<div class="mb20"></div><!-- space -->
				<h5>Submitter</h5>
				<div>${abstract["submitter_name"].decode('utf-8')}</div>
				<div class="mb20"></div><!-- space -->
				<h5>Abstract</h5>
				<div>${abstract["abstract_text"].decode('utf-8').replace("\n","<br/>")|n}</div>
				<div class="mb20"></div><!-- space -->
				<h5>Authors</h5>
					% for author in authors:
				<div class="row">
					<div class="col-xs-3">${author["fullname"].decode('utf-8')}</div>
					<div class="col-sm-3">${author["email"].decode('utf-8')}</div>
					<div class="col-sm-4">${author["institution"].decode('utf-8')}, 
						${fullCountryNameArray[author["country"]].decode('utf-8')}</div>
				</div>
					% endfor
				<div class="mb20"></div><!-- space -->
				<h5>Topics</h5>
				<div>${abstract["categories"][2:len(abstract["categories"])-2].replace("','",", ")}</div>
				<div class="mb20"></div><!-- space -->
				<!--
				## TODO: Add check to see if it is reviewed to allow it to select an editor
				-->
				% if user.is_admin():
					% if len(editors) > 0 and editors[0] != 0:
				<div class="row">
					<div class="col-md-6"><select id="selectedEditor" class="editor form-control" origEid="${editors[0]}" aid="${abstract['id']}"></select></div>
					<div class="col-md-6"><input type="button" class="btn btn-custom assignEditor" id="" value="Assign to Another Editor"/></div>
				</div>
					% else:
				<div class="row">
					<div class="col-md-6"><select id="selectedEditor" class="editor form-control" origEid="${editors[0]}" aid="${abstract['id']}"></select></div>
					<div class="col-md-6"><input type="button" class="btn btn-custom assignEditor" id="" value="Assign an Editor"/></div>
				</div>
					% endif
				% endif
				<!--
				## TODO: Reenable for next year
				<label>
				% if len(reviewers)>1:
				Reviewers
				% else:
				Assigned Reviewer
				% endif
				</label>
				% if len(reviewers) == 0:
					% if reviewersAvailable == True:
				<div>
				<select id="selectedReviewer" class="reviewer form-control" origRid="0" aid="${abstract['id']}"></select>
				<input type="button" class="btn btn-custom assignReviewer" id="" value="Assign Reviewer"/>
				</div>
				<div class="mb20"></div>
					% else:
					<div class='alert alert-danger'>No Reviewers for this abstract are available</div>
					% endif
				% else:
					% for reviewer in reviewers:
				<div class="row">
					<div class="col-md-6"><select id="selectedReviewer" class="reviewer form-control" origRid="${reviewer}" aid="${abstract['id']}"></select></div>
					<div class="col-md-6"><input type="button" class="btn btn-custom assignReviewer" id="" value="Assign to Another Reviewer"/></div>
				</div>
				<div class="mb20"></div>
					% endfor
				% endif
				-->
				<div style="position:relative;border-top:1px solid #000;border-bottom:1px solid #000; padding:10px 0px;margin-bottom:10px">
				% if user.is_reviewer() and user.chairId in reviewers:
				
				% else:
				<div style="position:absolute; top:0px;height: 100%; width:100%; background:rgba(225, 225, 225, .5)"></div>
				% endif
				<h4>Review Action</h4>
				<label class="input-desc">Select a score and session/category for this abstract</label>
				% if user.is_reviewer() and user.chairId in reviewers:
				<select class="form-control" id="score">
					<option value="">Select a Score</option>
					<option value="0">0 (Reject)</option>
					<option value="1">1 (Borderline Reject)</option>
					<option value="2">2 (Borderline Acceptable)</option>
					<option value="3">3 (Acceptable)</option>
					<option value="4">4 (Excellent)</option>
				</select>
				<select class="form-control" id="suggestedTopic">
					<option value="">Select a Session/Category</option>
					% if len(selectedTopics) > 0:
					<optgroup label="Selected Topics">
						% for i in range(len(selectedTopics)):
						<option value="${selectedTopics[i]['id']}">${selectedTopics[i]['label']}</option>
						% endfor
					</optgroup>
					% endif
					% for i in range(len(categoryNames)):
						% if len(categories[i]) > 0:
						<optgroup label="${categoryNames[i]}">
							% for j in range(len(categories[i])):
							<option value="${categories[i][j]['id']}">${categories[i][j]['label']}</option>
							% endfor
						</optgroup>
						% endif
					% endfor
				</select>
				<div>
				<label for="reviewerNotes">Notes for session chairs, conference organizers and proceeding editor</label>
				<textarea class="form-control" id="reviewerNotes"></textarea>
				</div>
				<input type="button" aid="${abstract["id"]}" class="btn btn-custom" id="saveScoreButton" value="Submit Review">
				% else:
				<select class="form-control" disabled>
					<option>Select a Score</option>
				</select>
				<select class="form-control" id="suggestedTopic" disabled>
					<option>Select a Session/Category</option>
				</select>
				% endif
				</div>
				<input type="button" class="btn btn-custom" value="Return to Abstracts" onclick="location.href='/dashboard'">
			</div>

		</div><!-- End .col-sm-12 -->

	</div><!-- End .row -->


<%include file="includes/contentFooter.mako"/>
<%include file="includes/pageFooter.mako"/>
<%include file="includes/pageEndScripts.mako"/>
<div id="modalConfirm" class="modal fade" role="dialog">
	<div class="modal-dialog">
		<!-- Modal content-->
		<div class="modal-content">
			<div class="modal-header">
				<button type="button" class="close" data-dismiss="modal">&times;</button>
				<h3 class="modal-title">WARNING</h3>
			</div>
			<div class="modal-body scrollPortlet">
				Please confirm that you want to assign this abstract to <span id="reviewerName"></span> (<span id="reviewerEmail"></span>). Control over review of this abstract will be given to <span id="reviewerName2"></span>.
			</div>
			<div class="modal-footer"><div class="pull-right"><input type="button" id="confirmReviewer" class="btn btn-custom2" aid="${abstract['id']}" value="Submit"><input type="button" data-dismiss="modal" class="btn btn-dark" value="Cancel"/></div></div>
		</div>
	</div>
</div>
<div id="modalConfirmRemoval" class="modal fade" role="dialog">
	<div class="modal-dialog">
		<!-- Modal content-->
		<div class="modal-content">
			<div class="modal-header">
				<button type="button" class="close" data-dismiss="modal">&times;</button>
				<h3 class="modal-title">WARNING</h3>
			</div>
			<div class="modal-body scrollPortlet">
				Please confirm that you want to remove <span id="reviewerRemovalName"></span> (<span id="reviewerRemovalEmail"></span>) from reviewing this abstract.
			</div>
			<div class="modal-footer"><div class="pull-right"><input type="button" id="confirmReviewerRemoval" class="btn btn-custom2" aid="${abstract['id']}" value="Submit"><input type="button" data-dismiss="modal" class="btn btn-dark" value="Cancel"/></div></div>
		</div>
	</div>
</div>
% if user.is_reviewer():
<div id="modalConfirmSaveScore" class="modal fade" role="dialog">
	<div class="modal-dialog">
		<!-- Modal content-->
		<div class="modal-content">
			<div class="modal-header">
				<button type="button" class="close" data-dismiss="modal">&times;</button>
				<h3 class="modal-title">WARNING</h3>
			</div>
			<div class="modal-body scrollPortlet">
				You have assigned the abstract titled <strong>${abstract["title"]}</strong> a score of <strong id="saveScore"></strong><span id="suggestedTopicSelected"> and have recommended a session/category of <strong id="saveTopic"></strong></span>.
			</div>
			<div class="modal-footer"><div class="pull-right"><input type="button" id="confirmSaveScore" class="btn btn-custom2" aid="${abstract['id']}" value="Submit Review"><input type="button" data-dismiss="modal" class="btn btn-dark" value="Cancel"/></div></div>
		</div>
	</div>
</div>
% elif user.is_admin():
<div id="modalConfirmEditor" class="modal fade" role="dialog">
	<div class="modal-dialog">
		<!-- Modal content-->
		<div class="modal-content">
			<div class="modal-header">
				<button type="button" class="close" data-dismiss="modal">&times;</button>
				<h3 class="modal-title">WARNING</h3>
			</div>
			<div class="modal-body scrollPortlet">
				Please confirm that you want to assign this abstract to <span id="editorName"></span> (<span id="editorEmail"></span>). Control over editing of this abstract will be given to <span id="editorName2"></span>.
			</div>
			<div class="modal-footer"><div class="pull-right"><input type="button" id="confirmEditor" class="btn btn-custom2" aid="${abstract['id']}" value="Submit"><input type="button" data-dismiss="modal" class="btn btn-dark" value="Cancel"/></div></div>
		</div>
	</div>
</div>
<div id="modalConfirmEditorRemoval" class="modal fade" role="dialog">
	<div class="modal-dialog">
		<!-- Modal content-->
		<div class="modal-content">
			<div class="modal-header">
				<button type="button" class="close" data-dismiss="modal">&times;</button>
				<h3 class="modal-title">WARNING</h3>
			</div>
			<div class="modal-body scrollPortlet">
				Please confirm that you want to remove <span id="editorRemovalName"></span> (<span id="editorRemovalEmail"></span>) from reviewing this abstract.
			</div>
			<div class="modal-footer"><div class="pull-right"><input type="button" id="confirmEditorRemoval" class="btn btn-custom2" aid="${abstract['id']}" value="Submit"><input type="button" data-dismiss="modal" class="btn btn-dark" value="Cancel"/></div></div>
		</div>
	</div>
</div>

% endif
<!--
% if user.is_admin():
Admin
% elif user.is_reviewer():
Reviewer
% elif user.is_editor():
Editor
% else:
Everyone Else
% endif
-->
</body>