<%inherit file="base.mako"/>

<div class="vis-heading">
    <div class="container">
        <div class="row">
        <div class="col-md-12">
            <h2>Welcome to ${request.registry.settings['jobs.sitename']}!</h2>
        </div></div>
    </div>
</div>

<div class="container">
    <div class="row">
        <div class="col-md-8">
            %if request.registry.settings.get('jobs.demo', '') == 'true':
            <p>${request.registry.settings['jobs.sitename']} is a demo site for Trimastone Consulting Ltd.</p><p>Login as demo@example.com / demopassword to post a listing.</p>
            %else:
            <p>${request.registry.settings['jobs.sitename']} is a service for connecting tech industry companies with talented tech industry workers. Here you can:</p>
            <ul>
                <li>Advertise tech jobs where people will see them.</li>
                <li>Find the best candidates.</li>
                <li>Find employment at a great company.</li>
            </ul>
            %endif
            <h2>Getting Started:</h2>
        </div>
        <div style="clear:left"></div>
        <div id="getting-started" class="col-md-4">
            <h4>Employers</h4>
            <a href="${request.route_path('addlisting_login')}"><button type="button" class="btn btn-primary btn-block btn-lg">Post a Listing</button></a>
        </div>
        <div class="col-md-4">
            <h4>Candidates</h4>
            <a href="${request.route_path('searchlistings')}"><button type="button" class="btn btn-primary btn-block btn-lg">Search Listings</button></a>
        </div>
    </div>
</div>
