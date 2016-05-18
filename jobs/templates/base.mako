<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <link rel="stylesheet" href="/static/jobs.css" type="text/css" />
    <link rel="stylesheet" href="/deform_static/css/form.css" type="text/css" />
    <script type="text/javascript" src="/deform_static/scripts/jquery-2.0.3.min.js"></script>
    <script type="text/javascript" src="/deform_static/scripts/deform.js"></script>
    
    <!-- The above 3 meta tags *must* come first in the head; any other head content must come *after* these tags -->
    <title>${request.registry.settings['jobs.sitename']}</title>

    <!-- Bootstrap -->
    <link href="/static/bootstrap-3.3.6-dist/css/bootstrap.min.css" rel="stylesheet">

    <!-- HTML5 shim and Respond.js for IE8 support of HTML5 elements and media queries -->
    <!-- WARNING: Respond.js doesn't work if you view the page via file:// -->
    <!--[if lt IE 9]>
      <script src="https://oss.maxcdn.com/html5shiv/3.7.2/html5shiv.min.js"></script>
      <script src="https://oss.maxcdn.com/respond/1.4.2/respond.min.js"></script>
    <![endif]-->
    
##    <script>
##  (function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
##  (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
##  m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
##  })(window,document,'script','//www.google-analytics.com/analytics.js','ga');
##  ga('create', 'UA-75802261-1', 'auto');
##  ga('send', 'pageview');
##   </script>
    
  </head>
  <body>
  <div class="wrap">
    <nav class="navbar navbar-default">
      <div class="container">
        <div class="navbar-header">
          <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#bs-example-navbar-collapse-1" aria-expanded="false">
            <span class="sr-only">Toggle navigation</span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
          </button>
          <a class="navbar-brand" href="${request.route_path('home')}">${request.registry.settings['jobs.sitename']}</a>
        </div>      
        <div class="collapse navbar-collapse" id="bs-example-navbar-collapse-1">
          <ul class="nav navbar-nav">
            <li><a href="${request.route_path('home')}">Home</a></li>
            <li><a href="${request.route_path('searchlistings')}">See Listings</a></li>
            <li><a href="${request.route_path('addlisting_login')}">Add Listing</a></li>
            <li><a href="${request.route_path('contact')}">Contact Us</a></li>
            %if request.authenticated_userid:
            <li><a href="${request.route_path('logout')}">Logout</a></li>
            %else:
            <li><a href="${request.route_path('login')}">Login</a></li>
            %endif
            
          </ul>
        </div>
      </div>
    </nav>
        
    ${self.body()}
    
    <footer class="jobs-footer">
      <div class="container">
          <p>Copyright 2016 Trimastone Technologies Ltd.</p>
      </div>
    </footer>

    <!-- jQuery (necessary for Bootstrap's JavaScript plugins) -->
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.3/jquery.min.js"></script>
    <!-- Include all compiled plugins (below), or include individual files as needed -->
    <script src="/static/bootstrap-3.3.6-dist/js/bootstrap.min.js"></script>
    </div>
  </body>
</html>
