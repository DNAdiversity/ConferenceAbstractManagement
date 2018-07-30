		<div id="content" role="main">
			<div class="page-header dark larger larger-desc">
				<div class="container">
					<div class="row">
						% if not pageTitle is UNDEFINED:
						<div class="col-md-6">
							<h1>${pageTitle|n}</h1>
							##<p class="page-header-desc">${pageDesc|n}</p>
						</div><!-- End .col-md-6 -->
						% endif
						<div class="col-md-6">
							% if not breadCrumbs is UNDEFINED and breadCrumbs is not None:
							##<ol class="breadcrumb">
								% for breadCrumb in breadCrumbs:
									##<% breadCrumbLink = '<a href="' + breadCrumb["url"] + '">' %>
									##<li${'' if loop.index < len(breadCrumbs) - 1 else ' class="active"'|n}>
									##	${breadCrumbLink if loop.index < len(breadCrumbs) - 1 else '' | n}${breadCrumb['text']}${'</a>' if loop.index < len(breadCrumbs) - 1 else '' |n}
									##</li>
								% endfor
							##</ol>
							% endif
						</div><!-- End .col-md-6 -->
					</div><!-- End .row -->
				</div><!-- End .container -->
			</div><!-- End .page-header -->

			<div class="container">