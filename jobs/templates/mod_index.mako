<%inherit file="base.mako"/>
<div class="container">
    <div class="row">
        <div class="col-md-12">
            <a href="${request.route_path('mod_listing')}">Moderate Listings</a><br/>
            <a href="${request.route_path('mod_application')}">Moderate Applications</a><br/>
        </div>
    </div>
</div>
