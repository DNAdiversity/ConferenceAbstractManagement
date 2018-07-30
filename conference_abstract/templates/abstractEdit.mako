<%inherit file='includes/base.mako' />
<%block name="header">

<script type="text/javascript">
	$(document).ready(function(){
		% for i in range(len(authors)):
		<% 
		author = authors[i] 
		%>
		$("#row${i} #country").val('${author["country"]}');
		% endfor
		$("#authors tbody .author").each(function(){
			var authorRow = $(this);
			authorRow.find("#presentingCheck").on("click",function(){
				if ($(this).prop("checked")==true){
					$("#presenting"+$(this).attr("row")).val("t");
				} else {
					$("#presenting"+$(this).attr("row")).val("f");
				}
			});
			authorRow.find("#correspondingCheck").on("click",function(){
				if ($(this).prop("checked")==true){
					$("#corresponding"+$(this).attr("row")).val("t");
					var currentlyChecked = $(this).attr("row");
					$("#authors .corresponding").each(function(){
						if ($(this).attr("row") != currentlyChecked){
							if ($(this).prop("checked")==true){
								/*
								## uncheck previously selected correspondent
								*/
								$(this).click();
							}
						}
					});
				} else {
					$("#corresponding"+$(this).attr("row")).val("f");
				}
			});
		});
		/*
		##addAuthor();
		##$("#row0 #presentingCheck").click();
		##$("#row0 #correspondingCheck").click();
		*/
		$("#submitAbstract").on("click",function(){
			if (validateSubmit() == false) {
				setTimeout(showErrors(),2000)
			}
		});
		$("body").on("keyup","#abstractText",function(){
			var info = wordCount($(this).val());
			var styleStart = "";
			var styleEnd = "";
			if (info.words>300){
				styleStart = "<b style='color:#f00'>";
				styleEnd = "</b>";
			}
			$("#abstractTextInfo").html("Words: "+styleStart+info.words+styleEnd);
		});
		
		
	});
	function showErrors(){
		$(window.opera ? 'html' : 'html, body').animate({
			scrollTop: 0
		}, 'slow');
	}
	function validateSubmit(){
		var validSubmit = true;
		var errors = [];
		var validCategory = false;
		var validPresentation = false;
		$("#divErrors").hide();
		/*
		## make sure all require fields are not empty
		*/
		$("#abstractForm .form-control").each(function(){
			if (typeof($(this).attr("required")) != 'undefined'){
				if ($.trim($(this).val()) == ""){
					validSubmit = false;
					errors[errors.length] = "Please fill out "+$(this).attr("placeholder");
				}
			}
		});
		var abstractInfo = wordCount($("#abstractText").val());
		if (abstractInfo.words > 300){
			validSubmit = false;
			errors[errors.length] = "Please shorten the abstract to 300 words";
		}
		/*
		## make sure one category is selected
		*/
		$(".category").each(function(){
			if ($(this).prop("checked")){
				validCategory = true
			}
		});
		if (validCategory == false){
			validSubmit = false;
			errors[errors.length] = "Please select at least 1 category";
		}
		/*
		## Make sure a presentation type is selected
		*/
		$(".preferredPresentation").each(function(){
			if ($(this).prop("checked")){
				validPresentation = true;
			}
		});
		if (validPresentation == false){
			validSubmit = false;
			errors[errors.length] = "A presentation type needs to be selected";
		}
		/*
		## make sure the first author is filled out
		*/
		var numOfAuthors = $("#authors tbody tr").length;
		var validAuthors = 0;
		var correspAuthors = 0;
		var presentingAuthors = 0;
		var submitter = 0;
		var invalidEmails = 0;
		var missingDetails = 0;
		var rowCount = 0;
		var missingDetailRows = [];
		var invalidEmailRows = [];
		$("#authors tbody .author").each(function(){
			rowCount++;
			if ($.trim($(this).prev().find("#firstname").val()) != "" &&
				$.trim($(this).prev().find("#lastname").val()) != "" &&
				$.trim($(this).prev().find("#email").val()) != "" &&
				$.trim($(this).prev().find("#institution").val()) != "" &&
				$.trim($(this).find("#country").val()) != ""){
				if (validateEmail($.trim($(this).prev().find("#email").val()))){
					validAuthors++;
					if ($(this).find("#correspondingCheck").prop("checked")){
						correspAuthors++;
					}
					if ($(this).find("#presentingCheck").prop("checked")){
						presentingAuthors++;
					}
					if ($.trim($(this).prev().find("#email").val()) == "${user.login}"){
						submitter++
					}
				} else {
					//all filled out but the email is invalid
					invalidEmails++;
					invalidEmailRows.push(rowCount);
				}
			} else if ($.trim($(this).prev().find("#firstname").val()) == "" &&
				$.trim($(this).prev().find("#lastname").val()) == "" &&
				$.trim($(this).prev().find("#email").val()) == "" &&
				$.trim($(this).prev().find("#institution").val()) == "" &&
				$.trim($(this).find("#country").val()) == "") {
				//Lets skip the blank lines
			} else {
				missingDetails++;
				missingDetailRows.push(rowCount);
			}
		});

		if (missingDetails > 0){
			var pluralAuthor = "";
			var plural = "is";
			if (missingDetails > 1){
				pluralAuthor = "s";
				plural = "are"
			}
			validSubmit = false;
			errors[errors.length] = missingDetails + " of the author"+pluralAuthor + " entries "+plural+" incomplete";
			/*
			##console.log(missingDetailRows);
			*/
		}

		if (invalidEmails > 0){
			var plural = "is";
			var pluralAuthor = "";
			if (invalidEmails > 1){
				plural = "are"
				pluralAuthor = "s";
			}
			validSubmit = false;
			errors[errors.length] = invalidEmails + " of the author"+pluralAuthor + " emails " + plural + " not valid";
			/*
			##console.log(invalidEmailRows);
			*/
		}

		if (submitter == 0){
			validSubmit = false;
			errors[errors.length] = "The submitter (you) must be one of the authors (based on email)";
		}
		
		if (validAuthors == 0 || correspAuthors == 0 || presentingAuthors == 0){
			validSubmit = false;
			if (validAuthors == 0){
				if (missingDetails == 0){
					errors[errors.length] = "One of the author entries is incomplete";
				}
			} else {
				if (correspAuthors == 0) {
					errors[errors.length] = "Please select the corresponding author";
				} 
				if (presentingAuthors == 0) {
					errors[errors.length] = "Please select the presenting author";
				}
			}
		}
		
		
		if (validSubmit == true){
			if (!$("#policy").prop("checked")){
				$("#modalConfirm").modal("show");
			} else {
				$("#abstractForm").submit();
			}
		} else {
			$("#errorList").empty();
			for (var i = 0; i < errors.length; i++){
				$("#errorList").append("<li>"+errors[i]+"</li>");
			}
			$("#divErrors").show();
		}
		return validSubmit;
	}

	function validateEmail(email) {
		var re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
		return re.test(email);
	}

	function wordCount( val ){
		var wom = val.match(/\S+/g);
		return {
			charactersNoSpaces : val.replace(/\s+/g, '').length,
			characters         : val.length,
			words              : wom ? wom.length : 0,
			lines              : val.split(/\r*\n/).length
		};
	}


	function addAuthor(){
		var currentRow = $(".author").length;
		var authorRow = $("#authorRow").clone().prop("id","row"+currentRow+"_");
		authorRow.find("#authNumber").text(currentRow+1);
		var authorRow2 = $("#authorRow2").clone().prop("id","row"+currentRow).addClass("author");
		authorRow2.find("#presenting").attr("id","presenting"+currentRow);
		authorRow2.find("#presentingCheck").attr("row",currentRow).on("click",function(){
			if ($(this).prop("checked")==true){
				$("#presenting"+$(this).attr("row")).val("t");
			} else {
				$("#presenting"+$(this).attr("row")).val("f");
			}
		});
		authorRow2.find("#corresponding").attr("id","corresponding"+currentRow)
		authorRow2.find("#correspondingCheck").attr("row",currentRow).on("click",function(){
			if ($(this).prop("checked")==true){
				$("#corresponding"+$(this).attr("row")).val("t");
				var currentlyChecked = $(this).attr("row");
				$("#authors .corresponding").each(function(){
					if ($(this).attr("row") != currentlyChecked){
						if ($(this).prop("checked")==true){
							/*
							## uncheck previously selected correspondent
							*/
							$(this).click();
						}
					}
				});
			} else {
				$("#corresponding"+$(this).attr("row")).val("f");
			}
		});

		$("#authors tbody").append(authorRow);
		$("#authors tbody").append(authorRow2);
	}
	
</script>
<style>
#authors tbody tr {
    background: #fff none repeat scroll 0 0;
	border:none;
}
#authors tbody td{
	border:none;
}
#authors tbody > tr > td:first-child {
    background-color: inherit;
}
#authors tbody tr:nth-child(4n-1), #authors tbody tr:nth-child(4n) {
    background: #fafafa none repeat scroll 0 0 !important;
	border:none;
}
	
</style>
</%block>
<body>
<%include file="includes/pageHeader.mako"/>
<%include file="includes/contentHeader.mako"/>

	<div class="row">
		<div class="col-sm-12">
			<form id="abstractForm" method="post"><a name="abstract"></a>
			<p>Please perform the following steps in order to save your abstract</p>
			<img src="/static/images/progess.png" class="img-responsive" alt="" />		

				<!--<div class="row">
					<div class="col-xs-3">
						<a href="#abstract" class="scrollto"><span class="fa-stack fa-md"><i class="fa fa-circle fa-stack-2x "></i><strong class="fa-stack-1x fa-inverse">1</strong></span> Abstract</a>
					</div>
					<div  class="col-xs-3">
						<a href="#cateogories" class="scrollto"><span class="fa-stack fa-md"><i class="fa fa-circle fa-stack-2x "></i><div class="fa-stack-1x fa-inverse">2</div></span> Session Topics</a>
					</div>
					<div class="col-xs-3">
						<a href="#author" class="scrollto"><span class="fa-stack fa-md"><i class="fa fa-circle fa-stack-2x "></i><div class="fa-stack-1x fa-inverse">3</div></span> Authors</a>
					</div>
				</div>-->


				<div class="alert alert-danger" style="display:none" id="divErrors">
					<strong>Errors:</strong> 
					<ul id="errorList">
					</ul>
				</div>
				<h2 class="title-border custom mb40">Abstract
				<small>All submissions must be in English.</small></h2>
				<div class="row">
					<div class="col-sm-12 mb0-xs">
						<h5>Preferred Presentation Type</h5>
					</div><!-- End .col-sm-12 -->
					<div class="col-sm-2">
						<input type="radio" class="preferredPresentation" name="abstractType" value="Talk" ${'checked' if abstract["abstract_type"] is not UNDEFINED and abstract["abstract_type"] == 'Talk' else ''} required> Talk&nbsp;&nbsp;<i class="fa fa-microphone first-color"></i>
					</div>
					<div class="col-sm-2">
						<input type="radio" class="preferredPresentation" name="abstractType" value="Poster" ${'checked' if abstract["abstract_type"] is not UNDEFINED and abstract["abstract_type"] == 'Poster' else ''} required> Poster&nbsp;&nbsp;<i class="fa fa-file-text-o first-color"></i>
					</div>
					<div class="col-sm-8">
						<input type="radio" class="preferredPresentation" name="abstractType" value="Lightning Talk" ${'checked' if abstract["abstract_type"] is not UNDEFINED and abstract["abstract_type"] == 'Lightning Talk' else ''} required> Lightning Talk&nbsp;&nbsp;<i class="fa fa-bolt first-color"></i> <small>(5 min presentation plus poster)</small>
					</div>
				</div><!-- End .row -->
				<div class="mb20"></div><!-- space -->

				<div class="row">
					<div class="col-sm-12">
						<div class="form-group">
							<h5>Title</h5>
							<input type="text" class="form-control" id="abstractTitle" maxlength="1000" name="abstractTitle" placeholder="Abstract Title" value="${abstract['title'] if abstract['title'] is not UNDEFINED else ''}" required>
						</div><!-- End .from-group -->
					</div><!-- End .col-sm-12 -->
				</div><!-- End .row -->

				<div class="row">
					<div class="col-sm-12 ">
						<div class="form-group">
							<h5>Abstract</h5>
							<textarea class="form-control" id="abstractText" rows="10" name="abstractText" placeholder="Abstract Text" required>${abstract['abstract_text'] if abstract['abstract_text'] is not UNDEFINED else ''}</textarea>
							<div id="abstractTextInfo"></div>
							<p>Please use a word processor to verify that the spelling and grammar is correct.</p>
						</div><!-- End .from-group -->
					</div><!-- End .col-sm-6 -->
				</div><!-- End .row -->
				<a name="cateogories"></a>
				<div class="mb20"></div><!-- space -->
				<h2 class="title-border custom mb40">Session Topics
				<small>Please choose up to 3 topics relevant to your abstract</small></h2>
				<div class="row">
					% for i in range(len(categoryNames)):
						<div class="col-md-4 col-sm-6">
							<h5>Category: ${categoryNames[i]|n}</h5>
							% for j in range(len(categories[i])):
							<div class="checkbox">
								<label><input type="checkbox" class="category" name="category[]" value="'${categories[i][j]['label']|n}'" ${'checked'  if categories[i][j]['label'] in abstract["categories"] else ''}>${categories[i][j]['label']|n}</label>
							</div>
							% endfor
						</div>
						% if (i+1)%3 == 0 and i>0:
				</div>
				<div class="row">
						% endif
					% endfor
				</div>
				<a name="author"></a>
				<div class="mb20"></div><!-- space -->
				<h2 class="title-border custom mb40">Authors
				<small>The submitter must be included in the author list</small></h2>
				<div class="row">
				<small class="pull-right"><b>P</b> - Presenting Author &nbsp;<b>C</b> - Corresponding Author</small>
				</div>
				<div class="row">
				<div class="table-responsive">
				<table id="authors" class="table table-condensed table-striped">
					<thead>
						<th></th>
						<th>First Name</th>
						<th>Initial</th>
						<th>Last Name</th>
						<th>Email</th>
						##<th>Country</th>
						<th>Institution</th>
						<th colspan="2" >Role</th>
					</thead>
					<tbody>
						% for i in range(len(authors)):
						<% 
						author = authors[i] 
						%>
						<tr>
							<td id="authNumber" rowspan="2">${i+1}</td>
							<td>
								<input type="text" style="width:200px" class="form-controlq" id="firstname" name="firstname[]" placeholder="First Name" value="${author['first_name'] if author['first_name'] else ''}"/>
							</td><!-- End .from-group -->
							<td >
								<input type="text" style="width:50px" class="form-controlq" id="initial" name="initial[]" placeholder="Initial" value="${author['middle_initial'] if author['middle_initial'] else ''}"/>
							</td><!-- End .from-group -->
							<td>
								##<label for="lastname" class="input-desc">Last Name</label>
								<input type="text" style="width:200px" class="form-controlq" id="lastname" name="lastname[]" placeholder="Last Name" value="${author['last_name'] if author['last_name'] else ''}"/>
							</td><!-- End .from-group -->
							<td>
								<input type="email" class="form-controlq" id="email" name="email[]" placeholder="Email" value="${author['email'] if author['email'] else ''}"/>
							</td><!-- End .from-group -->
							<td colspan="3">
								<input type="text" style="width:200px" class="form-controlq" id="institution" name="institution[]" placeholder="Institution Name" value="${author['institution'] if author['institution'] else ''}">
							</td><!-- End .from-group -->
						</tr><!-- End .row -->
						<tr id="row${i}" class="author">
							<td colspan="2"><input type="text"   style="width:300px" id="department" name="department[]" placeHolder="Department Name" value="${author['department'] if author['department'] else ''}"/></td>
							<td colspan="2"><input type="text" style="width:100%" id="address1" name="address[]" placeHolder="Institution Address" value="${author['address'] if author['address'] else ''}"/></td>
							<td>
								<select class="form-controlq" style="width:150px;" id="country" name="country[]">
									<option value="">Select Country</option>
									<option value="AF">Afghanistan</option>
									<option value="AL">Albania</option>
									<option value="DZ">Algeria</option>
									<option value="AS">American Samoa</option>
									<option value="AD">Andorra</option>
									<option value="AO">Angola</option>
									<option value="AI">Anguilla</option>
									<option value="AQ">Antarctica</option>
									<option value="AG">Antigua and Barbuda</option>
									<option value="AR">Argentina</option>
									<option value="AM">Armenia</option>
									<option value="AW">Aruba</option>
									<option value="AU">Australia</option>
									<option value="AT">Austria</option>
									<option value="AZ">Azerbaijan</option>
									<option value="BS">Bahamas</option>
									<option value="BH">Bahrain</option>
									<option value="BD">Bangladesh</option>
									<option value="BB">Barbados</option>
									<option value="BY">Belarus</option>
									<option value="BE">Belgium</option>
									<option value="BZ">Belize</option>
									<option value="BJ">Benin</option>
									<option value="BM">Bermuda</option>
									<option value="BT">Bhutan</option>
									<option value="BO">Bolivia, Plurinational State of</option>
									<option value="BQ">Bonaire, Sint Eustatius and Saba</option>
									<option value="BA">Bosnia and Herzegovina</option>
									<option value="BW">Botswana</option>
									<option value="BV">Bouvet Island</option>
									<option value="BR">Brazil</option>
									<option value="IO">British Indian Ocean Territory</option>
									<option value="BN">Brunei Darussalam</option>
									<option value="BG">Bulgaria</option>
									<option value="BF">Burkina Faso</option>
									<option value="BI">Burundi</option>
									<option value="KH">Cambodia</option>
									<option value="CM">Cameroon</option>
									<option value="CA">Canada</option>
									<option value="CV">Cape Verde</option>
									<option value="KY">Cayman Islands</option>
									<option value="CF">Central African Republic</option>
									<option value="TD">Chad</option>
									<option value="CL">Chile</option>
									<option value="CN">China</option>
									<option value="CX">Christmas Island</option>
									<option value="CC">Cocos (Keeling) Islands</option>
									<option value="CO">Colombia</option>
									<option value="KM">Comoros</option>
									<option value="CG">Congo</option>
									<option value="CD">Congo, the Democratic Republic of the</option>
									<option value="CK">Cook Islands</option>
									<option value="CR">Costa Rica</option>
									<option value="CI">Cote d'Ivoire</option>
									<option value="HR">Croatia</option>
									<option value="CU">Cuba</option>
									<option value="CW">Curaçao</option>
									<option value="CY">Cyprus</option>
									<option value="CZ">Czech Republic</option>
									<option value="DK">Denmark</option>
									<option value="DJ">Djibouti</option>
									<option value="DM">Dominica</option>
									<option value="DO">Dominican Republic</option>
									<option value="EC">Ecuador</option>
									<option value="EG">Egypt</option>
									<option value="SV">El Salvador</option>
									<option value="GQ">Equatorial Guinea</option>
									<option value="ER">Eritrea</option>
									<option value="EE">Estonia</option>
									<option value="ET">Ethiopia</option>
									<option value="FK">Falkland Islands (Malvinas)</option>
									<option value="FO">Faroe Islands</option>
									<option value="FJ">Fiji</option>
									<option value="FI">Finland</option>
									<option value="FR">France</option>
									<option value="GF">French Guiana</option>
									<option value="PF">French Polynesia</option>
									<option value="TF">French Southern Territories</option>
									<option value="GA">Gabon</option>
									<option value="GM">Gambia</option>
									<option value="GE">Georgia</option>
									<option value="DE">Germany</option>
									<option value="GH">Ghana</option>
									<option value="GI">Gibraltar</option>
									<option value="GR">Greece</option>
									<option value="GL">Greenland</option>
									<option value="GD">Grenada</option>
									<option value="GP">Guadeloupe</option>
									<option value="GU">Guam</option>
									<option value="GT">Guatemala</option>
									<option value="GG">Guernsey</option>
									<option value="GN">Guinea</option>
									<option value="GW">Guinea-Bissau</option>
									<option value="GY">Guyana</option>
									<option value="HT">Haiti</option>
									<option value="HM">Heard Island and McDonald Islands</option>
									<option value="VA">Holy See (Vatican City State)</option>
									<option value="HN">Honduras</option>
									<option value="HK">Hong Kong</option>
									<option value="HU">Hungary</option>
									<option value="IS">Iceland</option>
									<option value="IN">India</option>
									<option value="ID">Indonesia</option>
									<option value="IR">Iran, Islamic Republic of</option>
									<option value="IQ">Iraq</option>
									<option value="IE">Ireland</option>
									<option value="IM">Isle of Man</option>
									<option value="IL">Israel</option>
									<option value="IT">Italy</option>
									<option value="JM">Jamaica</option>
									<option value="JP">Japan</option>
									<option value="JE">Jersey</option>
									<option value="JO">Jordan</option>
									<option value="KZ">Kazakhstan</option>
									<option value="KE">Kenya</option>
									<option value="KI">Kiribati</option>
									<option value="KP">Korea, Democratic People's Republic of</option>
									<option value="KR">Korea, Republic of</option>
									<option value="KW">Kuwait</option>
									<option value="KG">Kyrgyzstan</option>
									<option value="LA">Lao People's Democratic Republic</option>
									<option value="LV">Latvia</option>
									<option value="LB">Lebanon</option>
									<option value="LS">Lesotho</option>
									<option value="LR">Liberia</option>
									<option value="LY">Libya</option>
									<option value="LI">Liechtenstein</option>
									<option value="LT">Lithuania</option>
									<option value="LU">Luxembourg</option>
									<option value="MO">Macao</option>
									<option value="MK">Macedonia, the former Yugoslav Republic of</option>
									<option value="MG">Madagascar</option>
									<option value="MW">Malawi</option>
									<option value="MY">Malaysia</option>
									<option value="MV">Maldives</option>
									<option value="ML">Mali</option>
									<option value="MT">Malta</option>
									<option value="MH">Marshall Islands</option>
									<option value="MQ">Martinique</option>
									<option value="MR">Mauritania</option>
									<option value="MU">Mauritius</option>
									<option value="YT">Mayotte</option>
									<option value="MX">Mexico</option>
									<option value="FM">Micronesia, Federated States of</option>
									<option value="MD">Moldova, Republic of</option>
									<option value="MC">Monaco</option>
									<option value="MN">Mongolia</option>
									<option value="ME">Montenegro</option>
									<option value="MS">Montserrat</option>
									<option value="MA">Morocco</option>
									<option value="MZ">Mozambique</option>
									<option value="MM">Myanmar</option>
									<option value="NA">Namibia</option>
									<option value="NR">Nauru</option>
									<option value="NP">Nepal</option>
									<option value="NL">Netherlands</option>
									<option value="NC">New Caledonia</option>
									<option value="NZ">New Zealand</option>
									<option value="NI">Nicaragua</option>
									<option value="NE">Niger</option>
									<option value="NG">Nigeria</option>
									<option value="NU">Niue</option>
									<option value="NF">Norfolk Island</option>
									<option value="MP">Northern Mariana Islands</option>
									<option value="NO">Norway</option>
									<option value="OM">Oman</option>
									<option value="PK">Pakistan</option>
									<option value="PW">Palau</option>
									<option value="PS">Palestinian Territory, Occupied</option>
									<option value="PA">Panama</option>
									<option value="PG">Papua New Guinea</option>
									<option value="PY">Paraguay</option>
									<option value="PE">Peru</option>
									<option value="PH">Philippines</option>
									<option value="PN">Pitcairn</option>
									<option value="PL">Poland</option>
									<option value="PT">Portugal</option>
									<option value="PR">Puerto Rico</option>
									<option value="QA">Qatar</option>
									<option value="RE">Réunion</option>
									<option value="RO">Romania</option>
									<option value="RU">Russian Federation</option>
									<option value="RW">Rwanda</option>
									<option value="BL">Saint Barthélemy</option>
									<option value="SH">Saint Helena, Ascension and Tristan da Cunha</option>
									<option value="KN">Saint Kitts and Nevis</option>
									<option value="LC">Saint Lucia</option>
									<option value="MF">Saint Martin (French part)</option>
									<option value="PM">Saint Pierre and Miquelon</option>
									<option value="VC">Saint Vincent and the Grenadines</option>
									<option value="WS">Samoa</option>
									<option value="SM">San Marino</option>
									<option value="ST">Sao Tome and Principe</option>
									<option value="SA">Saudi Arabia</option>
									<option value="SN">Senegal</option>
									<option value="RS">Serbia</option>
									<option value="SC">Seychelles</option>
									<option value="SL">Sierra Leone</option>
									<option value="SG">Singapore</option>
									<option value="SX">Sint Maarten (Dutch part)</option>
									<option value="SK">Slovakia</option>
									<option value="SI">Slovenia</option>
									<option value="SB">Solomon Islands</option>
									<option value="SO">Somalia</option>
									<option value="ZA">South Africa</option>
									<option value="GS">South Georgia and the South Sandwich Islands</option>
									<option value="SS">South Sudan</option>
									<option value="ES">Spain</option>
									<option value="LK">Sri Lanka</option>
									<option value="SD">Sudan</option>
									<option value="SR">Suriname</option>
									<option value="SJ">Svalbard and Jan Mayen</option>
									<option value="SZ">Swaziland</option>
									<option value="SE">Sweden</option>
									<option value="CH">Switzerland</option>
									<option value="SY">Syrian Arab Republic</option>
									<option value="TW">Taiwan, Province of China</option>
									<option value="TJ">Tajikistan</option>
									<option value="TZ">Tanzania, United Republic of</option>
									<option value="TH">Thailand</option>
									<option value="TL">Timor-Leste</option>
									<option value="TG">Togo</option>
									<option value="TK">Tokelau</option>
									<option value="TO">Tonga</option>
									<option value="TT">Trinidad and Tobago</option>
									<option value="TN">Tunisia</option>
									<option value="TR">Turkey</option>
									<option value="TM">Turkmenistan</option>
									<option value="TC">Turks and Caicos Islands</option>
									<option value="TV">Tuvalu</option>
									<option value="UG">Uganda</option>
									<option value="UA">Ukraine</option>
									<option value="AE">United Arab Emirates</option>
									<option value="GB">United Kingdom</option>
									<option value="US">United States</option>
									<option value="UM">United States Minor Outlying Islands</option>
									<option value="UY">Uruguay</option>
									<option value="UZ">Uzbekistan</option>
									<option value="VU">Vanuatu</option>
									<option value="VE">Venezuela, Bolivarian Republic of</option>
									<option value="VN">Viet Nam</option>
									<option value="VG">Virgin Islands, British</option>
									<option value="VI">Virgin Islands, U.S.</option>
									<option value="WF">Wallis and Futuna</option>
									<option value="EH">Western Sahara</option>
									<option value="YE">Yemen</option>
									<option value="ZM">Zambia</option>
									<option value="ZW">Zimbabwe</option>
								</select>
							</td><!-- End .from-group -->
							<td>
								<label><input type="checkbox" id="presentingCheck" row="${i}" title="Presenting" class=" value="t" ${'checked' if author["presenting"] == True else ''}><input type="hidden" id="presenting${i}" name="presenting[]" value="${'t' if author["presenting"] == True else 'f'}" > P</label>
							</td>
							<td>
								<label><input type="checkbox" class="corresponding" row="${i}" title="Corresponding" id="correspondingCheck" value="t" ${'checked' if author["corresponding"] == True else ''}><input type="hidden" id="corresponding${i}" name="corresponding[]" value="${'t' if author["corresponding"] == True else 'f'}"> C</label>
							</td>
						</tr>

						% endfor
					</tbody>
				</table>
				</div>
				</div>
				<div class="row">
					<div class="col-sm-12">
						<p>Note: First author is assumed to be the presenting & cooresponding author. Please revise prior to submission.</p>
						<input type="button" class="btn btn-primary" value="Add Author" onclick="addAuthor()"/>
					</div>
				</div>
				<div class="hidden">
					<table>
						<tr id="authorRow">
							<td id="authNumber" rowspan="2"></td>
							<td>
								<input type="text" style="width:200px" class="form-controlq" id="firstname" name="firstname[]" placeholder="First Name">
							</td><!-- End .from-group -->
							<td >
								<input type="text" style="width:50px" class="form-controlq" id="initial" name="initial[]" placeholder="Initial">
							</td><!-- End .from-group -->
							<td>
								##<label for="lastname" class="input-desc">Last Name</label>
								<input type="text" style="width:200px" class="form-controlq" id="lastname" name="lastname[]" placeholder="Last Name">
							</td><!-- End .from-group -->
							<td>
								<input type="email" class="form-controlq" id="email" name="email[]" placeholder="Email">
							</td><!-- End .from-group -->
							<td colspan="3">
								<input type="text" style="width:200px" class="form-controlq" id="institution" name="institution[]" placeholder="Institution Name">
							</td><!-- End .from-group -->
						</tr><!-- End .row -->
						<tr id="authorRow2">
							<td colspan="2"><input type="text"   style="width:300px" id="department" name="department[]" placeHolder="Department Name"/></td>
							<td colspan="2"><input type="text" style="width:100%" id="address1" name="address[]" placeHolder="Institution Address"/></td>
							<td>
								<select class="form-controlq" style="width:150px;" id="country" name="country[]">
									<option value="">Select Country</option>
									<option value="AF">Afghanistan</option>
									<option value="AL">Albania</option>
									<option value="DZ">Algeria</option>
									<option value="AS">American Samoa</option>
									<option value="AD">Andorra</option>
									<option value="AO">Angola</option>
									<option value="AI">Anguilla</option>
									<option value="AQ">Antarctica</option>
									<option value="AG">Antigua and Barbuda</option>
									<option value="AR">Argentina</option>
									<option value="AM">Armenia</option>
									<option value="AW">Aruba</option>
									<option value="AU">Australia</option>
									<option value="AT">Austria</option>
									<option value="AZ">Azerbaijan</option>
									<option value="BS">Bahamas</option>
									<option value="BH">Bahrain</option>
									<option value="BD">Bangladesh</option>
									<option value="BB">Barbados</option>
									<option value="BY">Belarus</option>
									<option value="BE">Belgium</option>
									<option value="BZ">Belize</option>
									<option value="BJ">Benin</option>
									<option value="BM">Bermuda</option>
									<option value="BT">Bhutan</option>
									<option value="BO">Bolivia, Plurinational State of</option>
									<option value="BQ">Bonaire, Sint Eustatius and Saba</option>
									<option value="BA">Bosnia and Herzegovina</option>
									<option value="BW">Botswana</option>
									<option value="BV">Bouvet Island</option>
									<option value="BR">Brazil</option>
									<option value="IO">British Indian Ocean Territory</option>
									<option value="BN">Brunei Darussalam</option>
									<option value="BG">Bulgaria</option>
									<option value="BF">Burkina Faso</option>
									<option value="BI">Burundi</option>
									<option value="KH">Cambodia</option>
									<option value="CM">Cameroon</option>
									<option value="CA">Canada</option>
									<option value="CV">Cape Verde</option>
									<option value="KY">Cayman Islands</option>
									<option value="CF">Central African Republic</option>
									<option value="TD">Chad</option>
									<option value="CL">Chile</option>
									<option value="CN">China</option>
									<option value="CX">Christmas Island</option>
									<option value="CC">Cocos (Keeling) Islands</option>
									<option value="CO">Colombia</option>
									<option value="KM">Comoros</option>
									<option value="CG">Congo</option>
									<option value="CD">Congo, the Democratic Republic of the</option>
									<option value="CK">Cook Islands</option>
									<option value="CR">Costa Rica</option>
									<option value="CI">Cote d'Ivoire</option>
									<option value="HR">Croatia</option>
									<option value="CU">Cuba</option>
									<option value="CW">Curaçao</option>
									<option value="CY">Cyprus</option>
									<option value="CZ">Czech Republic</option>
									<option value="DK">Denmark</option>
									<option value="DJ">Djibouti</option>
									<option value="DM">Dominica</option>
									<option value="DO">Dominican Republic</option>
									<option value="EC">Ecuador</option>
									<option value="EG">Egypt</option>
									<option value="SV">El Salvador</option>
									<option value="GQ">Equatorial Guinea</option>
									<option value="ER">Eritrea</option>
									<option value="EE">Estonia</option>
									<option value="ET">Ethiopia</option>
									<option value="FK">Falkland Islands (Malvinas)</option>
									<option value="FO">Faroe Islands</option>
									<option value="FJ">Fiji</option>
									<option value="FI">Finland</option>
									<option value="FR">France</option>
									<option value="GF">French Guiana</option>
									<option value="PF">French Polynesia</option>
									<option value="TF">French Southern Territories</option>
									<option value="GA">Gabon</option>
									<option value="GM">Gambia</option>
									<option value="GE">Georgia</option>
									<option value="DE">Germany</option>
									<option value="GH">Ghana</option>
									<option value="GI">Gibraltar</option>
									<option value="GR">Greece</option>
									<option value="GL">Greenland</option>
									<option value="GD">Grenada</option>
									<option value="GP">Guadeloupe</option>
									<option value="GU">Guam</option>
									<option value="GT">Guatemala</option>
									<option value="GG">Guernsey</option>
									<option value="GN">Guinea</option>
									<option value="GW">Guinea-Bissau</option>
									<option value="GY">Guyana</option>
									<option value="HT">Haiti</option>
									<option value="HM">Heard Island and McDonald Islands</option>
									<option value="VA">Holy See (Vatican City State)</option>
									<option value="HN">Honduras</option>
									<option value="HK">Hong Kong</option>
									<option value="HU">Hungary</option>
									<option value="IS">Iceland</option>
									<option value="IN">India</option>
									<option value="ID">Indonesia</option>
									<option value="IR">Iran, Islamic Republic of</option>
									<option value="IQ">Iraq</option>
									<option value="IE">Ireland</option>
									<option value="IM">Isle of Man</option>
									<option value="IL">Israel</option>
									<option value="IT">Italy</option>
									<option value="JM">Jamaica</option>
									<option value="JP">Japan</option>
									<option value="JE">Jersey</option>
									<option value="JO">Jordan</option>
									<option value="KZ">Kazakhstan</option>
									<option value="KE">Kenya</option>
									<option value="KI">Kiribati</option>
									<option value="KP">Korea, Democratic People's Republic of</option>
									<option value="KR">Korea, Republic of</option>
									<option value="KW">Kuwait</option>
									<option value="KG">Kyrgyzstan</option>
									<option value="LA">Lao People's Democratic Republic</option>
									<option value="LV">Latvia</option>
									<option value="LB">Lebanon</option>
									<option value="LS">Lesotho</option>
									<option value="LR">Liberia</option>
									<option value="LY">Libya</option>
									<option value="LI">Liechtenstein</option>
									<option value="LT">Lithuania</option>
									<option value="LU">Luxembourg</option>
									<option value="MO">Macao</option>
									<option value="MK">Macedonia, the former Yugoslav Republic of</option>
									<option value="MG">Madagascar</option>
									<option value="MW">Malawi</option>
									<option value="MY">Malaysia</option>
									<option value="MV">Maldives</option>
									<option value="ML">Mali</option>
									<option value="MT">Malta</option>
									<option value="MH">Marshall Islands</option>
									<option value="MQ">Martinique</option>
									<option value="MR">Mauritania</option>
									<option value="MU">Mauritius</option>
									<option value="YT">Mayotte</option>
									<option value="MX">Mexico</option>
									<option value="FM">Micronesia, Federated States of</option>
									<option value="MD">Moldova, Republic of</option>
									<option value="MC">Monaco</option>
									<option value="MN">Mongolia</option>
									<option value="ME">Montenegro</option>
									<option value="MS">Montserrat</option>
									<option value="MA">Morocco</option>
									<option value="MZ">Mozambique</option>
									<option value="MM">Myanmar</option>
									<option value="NA">Namibia</option>
									<option value="NR">Nauru</option>
									<option value="NP">Nepal</option>
									<option value="NL">Netherlands</option>
									<option value="NC">New Caledonia</option>
									<option value="NZ">New Zealand</option>
									<option value="NI">Nicaragua</option>
									<option value="NE">Niger</option>
									<option value="NG">Nigeria</option>
									<option value="NU">Niue</option>
									<option value="NF">Norfolk Island</option>
									<option value="MP">Northern Mariana Islands</option>
									<option value="NO">Norway</option>
									<option value="OM">Oman</option>
									<option value="PK">Pakistan</option>
									<option value="PW">Palau</option>
									<option value="PS">Palestinian Territory, Occupied</option>
									<option value="PA">Panama</option>
									<option value="PG">Papua New Guinea</option>
									<option value="PY">Paraguay</option>
									<option value="PE">Peru</option>
									<option value="PH">Philippines</option>
									<option value="PN">Pitcairn</option>
									<option value="PL">Poland</option>
									<option value="PT">Portugal</option>
									<option value="PR">Puerto Rico</option>
									<option value="QA">Qatar</option>
									<option value="RE">Réunion</option>
									<option value="RO">Romania</option>
									<option value="RU">Russian Federation</option>
									<option value="RW">Rwanda</option>
									<option value="BL">Saint Barthélemy</option>
									<option value="SH">Saint Helena, Ascension and Tristan da Cunha</option>
									<option value="KN">Saint Kitts and Nevis</option>
									<option value="LC">Saint Lucia</option>
									<option value="MF">Saint Martin (French part)</option>
									<option value="PM">Saint Pierre and Miquelon</option>
									<option value="VC">Saint Vincent and the Grenadines</option>
									<option value="WS">Samoa</option>
									<option value="SM">San Marino</option>
									<option value="ST">Sao Tome and Principe</option>
									<option value="SA">Saudi Arabia</option>
									<option value="SN">Senegal</option>
									<option value="RS">Serbia</option>
									<option value="SC">Seychelles</option>
									<option value="SL">Sierra Leone</option>
									<option value="SG">Singapore</option>
									<option value="SX">Sint Maarten (Dutch part)</option>
									<option value="SK">Slovakia</option>
									<option value="SI">Slovenia</option>
									<option value="SB">Solomon Islands</option>
									<option value="SO">Somalia</option>
									<option value="ZA">South Africa</option>
									<option value="GS">South Georgia and the South Sandwich Islands</option>
									<option value="SS">South Sudan</option>
									<option value="ES">Spain</option>
									<option value="LK">Sri Lanka</option>
									<option value="SD">Sudan</option>
									<option value="SR">Suriname</option>
									<option value="SJ">Svalbard and Jan Mayen</option>
									<option value="SZ">Swaziland</option>
									<option value="SE">Sweden</option>
									<option value="CH">Switzerland</option>
									<option value="SY">Syrian Arab Republic</option>
									<option value="TW">Taiwan, Province of China</option>
									<option value="TJ">Tajikistan</option>
									<option value="TZ">Tanzania, United Republic of</option>
									<option value="TH">Thailand</option>
									<option value="TL">Timor-Leste</option>
									<option value="TG">Togo</option>
									<option value="TK">Tokelau</option>
									<option value="TO">Tonga</option>
									<option value="TT">Trinidad and Tobago</option>
									<option value="TN">Tunisia</option>
									<option value="TR">Turkey</option>
									<option value="TM">Turkmenistan</option>
									<option value="TC">Turks and Caicos Islands</option>
									<option value="TV">Tuvalu</option>
									<option value="UG">Uganda</option>
									<option value="UA">Ukraine</option>
									<option value="AE">United Arab Emirates</option>
									<option value="GB">United Kingdom</option>
									<option value="US">United States</option>
									<option value="UM">United States Minor Outlying Islands</option>
									<option value="UY">Uruguay</option>
									<option value="UZ">Uzbekistan</option>
									<option value="VU">Vanuatu</option>
									<option value="VE">Venezuela, Bolivarian Republic of</option>
									<option value="VN">Viet Nam</option>
									<option value="VG">Virgin Islands, British</option>
									<option value="VI">Virgin Islands, U.S.</option>
									<option value="WF">Wallis and Futuna</option>
									<option value="EH">Western Sahara</option>
									<option value="YE">Yemen</option>
									<option value="ZM">Zambia</option>
									<option value="ZW">Zimbabwe</option>
								</select>
							</td><!-- End .from-group -->
							<td>
								<label><input type="checkbox" id="presentingCheck" title="Presenting" class=" value="t"><input type="hidden" id="presenting" name="presenting[]" value="f"></label>
							</td>
							<td>
								<label><input type="checkbox" class="corresponding" title="Corresponding" id="correspondingCheck" value="t"><input type="hidden" id="corresponding" name="corresponding[]" value="f"></label>
							</td>
						</tr>
					</table>
				</div><!-- End Hidden -->
				<div class="mb20"></div><!-- space -->
				<hr/>
				<a name="save"></a>
				<div class="mb20"></div><!-- space -->
				<h2 class="title-border custom mb40">Save
				<small>After saving you will have a final chance to review before submission</small></h2>
	
				<div class="form-group mt15-r">
                                <div class="checkbox">
                                  <label class="custom-checkbox-wrapper">
                                    <span class="custom-checkbox-container">
                                        <input type="checkbox" name="policy" id="policy" value="true">
                                        <span class="custom-checkbox-icon"></span>
                                    </span>
                                   <span>I have verfied that the spelling and grammar is correct.</span>
                                  </label>
                                </div><!-- End .checkbox -->
                            </div><!-- End .form-group -->
				<div class="form-group mb5">
					<input type="button" id="submitAbstract" class="btn btn-custom" name="submitAbstract" value="Save Abstract">
				</div><!-- End .from-group -->
				<input type="hidden" name="abstractId" value="${abstractId if not abstractId is UNDEFINED else '0'}"/>
			</form>

		</div><!-- End .col-sm-12 -->

	</div><!-- End .row -->


<%include file="includes/contentFooter.mako"/>
<%include file="includes/pageFooter.mako"/>
<div id="modalConfirm" class="modal fade" role="dialog">
    <div class="modal-dialog">
        <!-- Modal content-->
        <div class="modal-content">
            <div class="modal-header">
                <button type="button" class="close" data-dismiss="modal">&times;</button>
                <h3 class="modal-title">WARNING</h3>
            </div>
            <div class="modal-body scrollPortlet">
				Please confirm that the spelling and grammar is correct and then check the box as indicated in the picture below. <br><br>
				<img src="/static/images/confirm.png" width="90%" class="img-responsive" style="border: 1px solid #eee;" alt="" />
				
            </div>
            <div class="modal-footer"><div class="pull-right"><input type="button" data-dismiss="modal" class="btn btn-dark" value="OK"/></div></div>
        </div>
    </div>
</div>

<%include file="includes/pageEndScripts.mako"/>
</body>