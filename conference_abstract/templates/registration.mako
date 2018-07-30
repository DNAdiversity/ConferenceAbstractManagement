<%inherit file='includes/base.mako' />
<%block name="header">
	<link rel="stylesheet" href="/static/css/bootstrap-datetimepicker.min.css">
	<script src="/static/js/bootstrap-datetimepicker.js"></script>
	<script type="text/javascript">
		var validEmail = false;
		$(document).ready(function(){
			$("#email").on("blur",function(){
				var emailToCheck = $.trim($(this).val());
				$.ajax({
					url:"/users/"+emailToCheck,
					method:"GET",
					dataType: 'text json',
					cache: false
				}).done(function(data){
					if(data["success"] == false){
						validEmail = true;
					} else {
						validEmail = false;
					}
				});
			});

			$("#btnRegister").on("click",function(){
				if (validateSubmit() == false) {
					setTimeout(showErrors(),2000)
				}
			});

			function showErrors(){
				$(window.opera ? 'html' : 'html, body').animate({
					scrollTop: 0
				}, 'slow');
			}
		
			function validateSubmit(){
				var validSubmit = true;
				var errors = [];
				$("#divErrors").hide();
				/*
				## make sure all require fields are not empty
				*/
				$("#formRegister .form-control").each(function(){
					if (typeof($(this).attr("required")) != 'undefined'){
						if ($.trim($(this).val()) == ""){
							validSubmit = false;
							errors[errors.length] = "Please fill out "+$(this).attr("placeholder");
						}
					}
				});
				## now check that email addresses are the same
				if ( $.trim($("#email").val()) != $.trim($("#remail").val()) ){
					validSubmit = false;
					errors[errors.length] = "Your emails do not match please enter them again";
				}
				## now check that the email doesn't exist
				if (validEmail == false){
					validSubmit = false;
					errors[errors.length] = "That email has already been registered."
				}
				if (!validateEmail($.trim($("#email").val()))){
					validSubmit = false;
					errors[errors.length] = "Please enter a valid email address."
				}
				if (validSubmit == true){
					$("#formRegister").submit();
				} else {
					$("#errorList").empty();
					for (var i = 0; i < errors.length; i++){
						$("#errorList").append("<li>"+errors[i]+"</li>");
					}
					$("#divErrors").show();
				}
				return validSubmit;
			}
		});
		function validateEmail(email) {
			var re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
			return re.test(email);
		}

	</script>
</%block>
<body>
<%include file="includes/pageHeader.mako"/>
<%include file="includes/contentHeader.mako"/>

	<div class="row">
		<div class="col-sm-12">
			<h2 class="title-border custom mb40">Create an Account</h2>
			<div class="alert alert-danger" style="display:none" id="divErrors">
				<strong>Errors:</strong> 
				<ul id="errorList">
				</ul>
			</div>
			<form id="formRegister" action="#" method="post" onsubmit="">
				<div class="row">
					<div class="col-sm-1">
						<div class="form-group">
							<label for="salutation" class="input-desc">Preferred<br/> Title</label>
							<select class="form-control" name="salutation" placeholder="salutation">
								<option value="">Select</option>
								<option value="Dr.">Dr.</option>
								<option value="Prof.">Prof.</option>
								<option value="Mrs.">Mrs.</option>
								<option value="Mr.">Mr.</option>
								<option value="Ms.">Ms.</option>
							</select>
						</div><!-- End .from-group -->
					</div><!-- End .col-sm-1 -->
					<div class="col-sm-4">
						<div class="form-group">
							<label for="firstname" class="input-desc">First<br/> Name</label>
							<input type="text" maxlength="128" class="form-control" id="firstname" name="firstname" placeholder="First Name" required>
						</div><!-- End .from-group -->
					</div><!-- End .col-sm-4 -->
					<div class="col-sm-1">
						<div class="form-group">
							<label for="middleinitial" class="input-desc">Middle Initial(s)</label>
							<input type="text" maxlength="5" class="form-control" id="middleinitial" name="middleinitial" placeholder="Initial">
						</div><!-- End .from-group -->
					</div><!-- End .col-sm-1 -->
					<div class="col-sm-6 ">
						<div class="form-group">
							<label for="lastname" class="input-desc">Last<br/> Name</label>
							<input type="text" maxlength="128" class="form-control" id="lastname" name="lastname" placeholder="Last Name" required>
						</div><!-- End .from-group -->
					</div><!-- End .col-sm-6 -->
				</div><!-- End .row -->

				<div class="row">
					<div class="col-sm-6 ">
						<div class="form-group">
							<label for="email" class="input-desc">Email (Institutional email address preferred)</label>
							<input type="email" maxlength="256" class="form-control" id="email" name="email" placeholder="Email" required>
						</div><!-- End .from-group -->
					</div><!-- End .col-sm-6 -->
					<div class="col-sm-6 ">
						<div class="form-group">
							<label for="remail" class="input-desc">Re-type Email</label>
							<input type="email" maxlength="256" class="form-control" id="remail" name="remail" placeholder="Re-type Email" required>
						</div><!-- End .from-group -->
					</div><!-- End .col-sm-6 -->
				</div><!-- End .row -->

				<div class="row">
				<h3>Institution Information</h3>
					<div class="col-sm-12 ">
						<div class="form-group">
							<label for="institution" class="input-desc">Institution Name</label>
							<input type="text" maxlength="256" class="form-control" id="institution" name="institution" placeholder="Institution Name" required>
						</div><!-- End .from-group -->
					</div><!-- End .col-sm-12 -->
					<div class="col-sm-12 ">
						<div class="form-group">
							<label for="institution" class="input-desc">Department</label>
							<input type="text" maxlength="256" class="form-control" id="department" name="department" placeholder="Department Name" required>
						</div><!-- End .from-group -->
					</div><!-- End .col-sm-12 -->
					
					<div class="col-sm-6 ">
						<div class="form-group">
							<label for="address1" class="input-desc">Address 1</label>
							<input type="text" maxlength="256" class="form-control" id="address1" name="address1" placeholder="Address 1" required>
						</div><!-- End .from-group -->
					</div><!-- End .col-sm-6 -->
					<div class="col-sm-6 ">
						<div class="form-group">
							<label for="address2" class="input-desc">Address 2</label>
							<input type="text" maxlength="256" class="form-control" id="address2" name="address2" placeholder="Address 2">
						</div><!-- End .from-group -->
					</div><!-- End .col-sm-6 -->
				<div class="col-sm-6 ">
						<div class="form-group">
							<label for="city" class="input-desc">City</label>
							<input type="text" maxlength="128" class="form-control" id="city" name="city" placeholder="City" required>
						</div><!-- End .from-group -->
					</div><!-- End .col-sm-6 -->
					<div class="col-sm-6 ">
						<div class="form-group">
							<label for="province_state" class="input-desc">Province/State</label>
							<input type="text" maxlength="128" class="form-control" id="province_state" name="province_state" placeholder="Province/State">
						</div><!-- End .from-group -->
					</div><!-- End .col-sm-6 -->					
					<div class="col-sm-6 ">
						<div class="form-group">
							<label for="postalcode" class="input-desc">Postal Code/Zip Code</label>
							<input type="text" maxlength="128" class="form-control" id="postalcode" name="postalcode" placeholder="Postal Code/Zip Code">
						</div><!-- End .from-group -->
					</div><!-- End .col-sm-6 -->					


					<div class="col-sm-6 ">
						<div class="form-group">
							<label class="input-desc">Country</label>
							<select class="form-control" name="country" placeholder="Country" required>
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
						</div><!-- End .from-group -->
					</div><!-- End .col-sm-6 -->
				</div><!-- End .row -->

				<div class="mb20"></div><!-- space -->

				<div class="form-group mb5">
					<input type="button" id="btnRegister" class="btn btn-custom" name="Register" value="Create Account"><input type="submit" style="display:none"/>
				</div><!-- End .from-group -->

			</form>

		</div><!-- End .col-sm-12 -->

	</div><!-- End .row -->


<%include file="includes/contentFooter.mako"/>
<%include file="includes/pageFooter.mako"/>
<%include file="includes/pageEndScripts.mako"/>
</body>