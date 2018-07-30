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
<script src="/static/js/tinymce/tinymce.min.js"></script>

<script type="text/javascript">
	$(document).ready(function(){
		var selectedAuthor = 0;
		$("#uploadAttachmentButton").on("click",function(){
			var files = $("#abstractAttachment").prop("files")
			if (!files.length){
				alert("Please select a file to upload!");
			} else {
				var f = files[0];
				var parseFilename = f.name.split(".");
				var goodFile = false;
				if (parseFilename[parseFilename.length-1].toLowerCase() == "pdf"){
					goodFile = true;
				}
				if (goodFile == true){
					$("#posterFilename").text(f.name);
					$("#modalConfirmUpload").modal("show");
				} else {
					alert("Please select a PDF file to upload!");
				}
			}
		});
		$("#confirmUpload").on("click",function(){
			$("#abstractUpload").submit();
		});
	});//end document.ready
</script>
<style>
	.greyout {
		color:#9f9f9f;
	}
</style>
</%block>
<%!
import unicodedata
%>
<body>
<%include file="includes/pageHeaderPoster.mako"/>
<%include file="includes/contentHeader.mako"/>
	<div class="row">
		<div class="col-sm-12">
			<h2 class="title-border custom mb40">Abstract Poster Uploader</h2>
			<p>Please upload a pdf poster for this abstract</p>
			<div>
				<h5>Poster ID</h5>
				<div>${abstract["id"]}</div>
				<div class="mb20"></div><!-- space -->
				<h5>Title</h5>
				<div>${abstract["title"].decode('utf-8')}</div>
				<div class="mb20"></div><!-- space -->
				<h5>Presentation Type</h5>
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
				<h5>Abstract</h5>
				<fieldset>
					<legend>Edited Version</legend>
					<div class="row">
						<div class="col-sm-12">
							% if abstract["abstract_text_edited"] == '':
							${abstract["abstract_text"].decode('utf-8').replace("\n","<br/>")|n}
							% else:
							${abstract["abstract_text_edited"].decode('utf-8').replace("\n","<br/>")|n}
							% endif
							<br/>Authors: <i>${abstract["authors"].decode('utf-8')|n}</i><br/><br/>
							<form method="post" enctype="multipart/form-data" id="abstractUpload">
							<h5>Poster Upload</h5>
							<div class="row">
								<div class="col-xs-12"><input type="file" name="abstractAttachment" accept="application/pdf" id="abstractAttachment" class="input-sm"/></div>
							</div>
							<div class="mb20"></div><!-- space -->
							<p>
								<input type="button" aid="${abstractIdEncoded}" class="btn btn-custom" id="uploadAttachmentButton" value="Upload"/>
							</p>
							</form>
						</div>
					</div>
				</fieldset>
			</div>

		</div><!-- End .col-sm-12 -->

	</div><!-- End .row -->


<%include file="includes/contentFooter.mako"/>
<%include file="includes/pageFooter.mako"/>
<%include file="includes/pageEndScripts.mako"/>
<div id="modalConfirmUpload" class="modal fade" role="dialog">
	<div class="modal-dialog">
		<!-- Modal content-->
		<div class="modal-content">
			<div class="modal-header">
				<button type="button" class="close" data-dismiss="modal">&times;</button>
				<h3 class="modal-title">WARNING</h3>
			</div>
			<div class="modal-body scrollPortlet">
				Are you sure you want to upload?  You are about to upload <b><span id="posterFilename"></span></b> as the poster for this abstract. You will not be able to edit the poster unless you contact <a href="mailto:abstracts@ibol.org">abstracts@ibol.org</a>.
			</div>
			<div class="modal-footer"><div class="pull-right"><input type="button" id="confirmUpload" class="btn btn-custom2" aid="${abstractIdEncoded}" value="Upload"><input type="button" data-dismiss="modal" class="btn btn-dark" value="Cancel"/></div></div>
		</div>
	</div>
</div>

</body>