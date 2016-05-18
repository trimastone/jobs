<%inherit file="base.mako"/>

<div class="container">
    <div class="row">
        <div class="col-md-12">
            <h1>Listings</h1>
        </div>
        <div class="col-md-12">
            <hr />
            %if len(listings) > 0:
            %for listing in listings:
            <div class="col-md-12 search-listing">
                <a href="${request.route_path('showlisting', listing_id=listing.listing_id, listing_title=listing.safeTitle())}"><h3>${listing.title}</h3></a>
                ${listing.user.company.name} - ${listing.location}
            </div>
            %endfor
            %else:
            <div class="col-md-12">
                <div class="alert alert-warning" role="alert">There are currently no listings.</div>
            </div>
            %endif
        </div>
        <div class="col-md-4">
            
        </div>
    </div>
</div>
