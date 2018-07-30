<%inherit file='includes/base.mako' />
<body>
	<div id="login-section" class="fullheight">
		<div class="vcenter-container">
			<div class="vcenter">
				<div class="container">
					<div class="row">
						<div class="col-sm-6 col-sm-push-3 col-lg-4 col-lg-push-4">
							<h1 class="logo text-center">
								<a href="/">
									<img src="/static/images/logo.png" alt="Logo">
								</a>
							</h1>
							<div class="form-wrapper">
								<div class="alert alert-info">
									Login is restricted to reviewers and conference coordinators only. <p> For the Poster Submission Portal click <u><a href="/loginPoster">here</a></u></p>
								</div>
								% if not pageTitle is UNDEFINED:
								<h2 class="title-underblock custom mb30">${pageTitle}</h2>
								% else:
								<h2 class="title-underblock custom mb30">Login</h2>
								% endif
								## show any error
								% if not message is UNDEFINED and message is not None:
								<div class="alert alert-danger">
									${message |n}
								</div>
								% endif
								<form method="post">
									<div class="form-group">
										<label for="login" class="input-desc">Email</label>
										<input type="text" class="form-control" id="login" name="login" value="" placeholder="Email" required>
									</div><!-- End .from-group -->
									<div class="form-group mb10">
										<label for="passwd" class="input-desc">Password</label>
										<input type="password" class="form-control" id="passwd" name="passwd" placeholder="Password" required>
									</div><!-- End .from-group -->
									<div class="form-group text-right clear-margin helper-group hidden">
										<a href="recover-password.html" class="add-tooltip" data-placement="top" title="Recover your password">Forgot password?</a>
									</div><!-- End .form-group -->
									<div class="form-group mt15-r">
										<div class="hidden">
										  <label class="custom-checkbox-wrapper">
											<span class="custom-checkbox-container">
												<input type="checkbox" name="remember" id="remember" value="true">
												<span class="custom-checkbox-icon"></span>
											</span>
										   <span>Remember Me!</span>
										  </label>
										</div><!-- End .checkbox -->
									</div><!-- End .form-group -->
									<div class="row">
										<input type="submit" name="submit" class="btn btn-custom" value="Login Now"><br><br><hr><br>
										<input type="button" class="btn btn-custom btn-border" value="Create Account" onclick="location.href='/registration'">
									</div>
								</form>
							</div><!-- End .form-wrapper -->
						</div><!-- End .col-sm-6 -->
					</div><!-- End .row -->
				</div><!-- End .container -->
			</div><!-- End .vcenter -->
		</div><!-- End .vcenter-container -->
	</div><!-- End .fullheight -->
<%include file="includes/pageEndScripts.mako"/>
</body>