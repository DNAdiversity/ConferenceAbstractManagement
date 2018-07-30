## Change Log:
	<div id="wrapper">
		<header id="header" role="banner">
			<div class="collapse navbar-white" id="header-search-form">
				<div class="container">
					<form class="navbar-form animated fadeInDown" >
						<input type="search" id="s" name="s" class="form-control" placeholder="Search in here...">
						<button type="submit" class="btn-circle" title="Search"><i class="fa fa-search"></i></button>
					</form>
				</div><!-- End .container -->
			</div><!-- End #header-search-form -->
			<nav class="navbar navbar-white animated-dropdown ttb-dropdown" role="navigation">

				<div class="navbar-top clearfix">
					<div class="container">
						<div class="pull-left">
							<ul class="navbar-top-nav clearfix hidden-xs">
								% if user is UNDEFINED or user is None:
								<li role="presentation"><a role="menuitem" tabindex="-1" href="/"><i class="fa fa-home"></i>Home</a></li>
								<li><a href="/registration"><i class="fa fa-edit"></i>Create Account</a></li>
								<li role="presentation"><a role="menuitem" tabindex="-1" href="/login"><i class="fa fa-external-link"></i>Login</a></li>
								% else:
								<li role="presentation"><a role="menuitem" tabindex="-1" href="/"><i class="fa fa-home"></i>Home</a></li>
									% if user.is_admin():
								<li role="presentation"><a role="menuitem" tabindex="-1" href="/dashboardPoster"><i class="fa fa-user"></i>Submitted Abstracts</a></li>
									% elif user.is_reviewer():
								<li role="presentation"><a role="menuitem" tabindex="-1" href="/dashboard"><i class="fa fa-user"></i>Assigned Abstracts</a></li>
									% else:
								<li role="presentation"><a role="menuitem" tabindex="-1" href="/dashboardPoster"><i class="fa fa-user"></i>My Abstracts</a></li>
									% endif
								<li role="presentation"><a role="menuitem" tabindex="-1" href="/logout"><i class="fa fa-external-link"></i>Logout</a></li>
								% endif
								
								<li><a href="/contactus"><i class="fa fa-info"></i>Contact Us</a></li>
							</ul>
							<ul class="navbar-top-nav clearfix visible-xs">
								% if user is UNDEFINED or user is None:
								<li role="presentation"><a role="menuitem" tabindex="-1" href="/"><i class="fa fa-home"></i>Home</a></li>
								% else:
								<li role="presentation"><a role="menuitem" tabindex="-1" href="/"><i class="fa fa-home"></i>Home</a></li>
								% endif
								
							</ul>
						</div><!-- End .pull-left -->
						<div class="pull-right">
							<div class="dropdowns-container pull-right clearfix visible-xs">
								<button type="button" class="navbar-toggle btn btn-small pull-right collapsed" data-toggle="collapse" data-target="#extra-menu" aria-expanded="false" style="margin: 5px">
									<span class="sr-only">Toggle navigation</span>
									<span class="icon-bar"></span>
								</button>
							</div>
						</div>
					</div><!-- End .container -->
				</div><!-- End .navbar-top -->
				<div class="visible-xs">
					<div class="navbar-collapse collapse" id="extra-menu" aria-expanded="true" style="">
						<ul class="nav navbar-nav">
							% if user is UNDEFINED or user is None:
								<li><a href="/registration"><i class="fa fa-edit"></i> Create Account</a></li>
								<li><a role="menuitem" tabindex="-1" href="/login"><i class="fa fa-external-link"></i> Login</a></li>
							% else:
								<li><a role="menuitem" tabindex="-1" href="/dashboard"><i class="fa fa-user"></i> My Abstracts</a></li>
								<li><a role="menuitem" tabindex="-1" href="/logout"><i class="fa fa-external-link"></i> Logout</a></li>
							% endif
							<li><a href="/contactus"><i class="fa fa-info"></i> Contact Us</a></li>
						</ul>
					</div>
				</div>
				<div class="navbar-inner sticky-menu">
					<div class="container">
						<div class="navbar-header">
							<a class="navbar-brand text-uppercase" href="/" title="">Conference Abstracts</a>
						</div><!-- End .navbar-header -->
						<div class="text-right" id="main-navbar-container">
							<span style="height:100%;display: inline-block; vertical-align: middle"></span>
							<img src="/static/images/croppedlogo_300.png" alt="Logo" style="vertical-align: middle;">
						</div>

					</div><!-- /.container -->
				</div><!-- End .navbar-inner -->
			</nav>
		</header><!-- End #header -->

