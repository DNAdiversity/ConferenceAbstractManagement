<%inherit file='includes/base.mako' />
<%block name="header">
</%block>
<script type="text/javascript">
	$(document).ready(function(){
		$("#submitMessage").on("click",function(){
			var validMessage = true;
			var errors = [];
			$("#contactForm .form-control").each(function(){
				if ($.trim($(this).val())==""){
					errors.push($(this).attr("placeholder")+" is empty.");
					validMessage = false;
				}
			});
			if (validMessage == true){
				$("#divErrors").hide();
				$("#contactForm").submit();
			} else {
				$("#divErrors").hide();
				$("#errorList").empty();
				for (var i = 0; i < errors.length; i++){
					$("#errorList").append("<li>" + errors[i] + "</li>")
				}
				$("#divErrors").show();
			}
		});
	});

</script>
<body>
<%include file="includes/pageHeader.mako"/>
<%include file="includes/contentHeader.mako"/>

		<div class="container">
			<div class="row">

				<div class="col-sm-8">
					<div class="alert alert-danger" style="display:none" id="divErrors">
						<strong>Errors:</strong> 
						<ul id="errorList">
						</ul>
					</div>
					<h2 class="title-underblock dark mb30">Contact Us</h2>
					<form method="post" id="contactForm">
						<div class="row">
							<div class="col-md-6">
								<div class="form-group">
									<label for="contactname" class="input-desc">First Name</label>
									<input type="text" class="form-control" id="contactname" name="contactname" placeholder="First Name" required>
								</div><!-- End .from-group -->
							</div><!-- End .col-md-6 -->
							<div class="col-md-6">
								<div class="form-group">
									<label for="contactlastname" class="input-desc">Last Name</label>
									<input type="text" class="form-control" id="contactlastname" name="contactlastname" placeholder="Last Name">
								</div><!-- End .from-group -->
							</div><!-- End .col-md-6 -->
						</div><!-- End .row -->
						<div class="row">
							<div class="col-md-6">
								<div class="form-group">
									<label for="contactemail" class="input-desc">Email</label>
									<input type="email" class="form-control" id="contactemail" name="contactemail" placeholder="Email" required>
								</div><!-- End .from-group -->
							</div><!-- End .col-md-6 -->
							<div class="col-md-6">
								<div class="form-group">
									<label for="contactsubject" class="input-desc">Subject</label>
									<input type="text" class="form-control" id="contactsubject" name="contactsubject" placeholder="Subject">
								</div><!-- End .from-group -->
							</div><!-- End .col-md-6 -->
						</div><!-- End .row -->
						<div class="row">
							<div class="col-md-12">
								<div class="form-group">
									<label for="contactmessage" class="input-desc">Message</label>
									<textarea class="form-control" rows="6" id="contactmessage" name="contactmessage" placeholder="Your Message" required></textarea>
								</div><!-- End .from-group -->
								<!--<div class="form-group">
									<div class="checkbox">
									  <label class="custom-checkbox-wrapper">
										<span class="custom-checkbox-container">
											<input type="checkbox" name="contactselfemail" value="True">
											<span class="custom-checkbox-icon"></span>
										</span>
									   <span>Send a copy to my e-mail address!</span>
									  </label>
									</div><!-- End .checkbox -->
								</div><!-- End .form-group -->

								<div class="mb5"></div><!-- space -->

								<div class="form-group">
								<input type="button" id="submitMessage" class="btn btn-dark min-width" data-loading-text="Sending..." value="Send Message">
								</div><!-- End .from-group -->
							</div><!-- End .col-md-12 -->
						</div><!-- End .row -->
					</form>
				</div><!-- End .col-sm-8 -->

		</div><!-- End .container -->



<%include file="includes/contentFooter.mako"/>
<%include file="includes/pageFooter.mako"/>
<%include file="includes/pageEndScripts.mako"/>
</body>