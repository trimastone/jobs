<%inherit file="base.mako"/>
<div class="container">
    <div class="row">
        %for listing in listing_list:
        <h1>${listing.title}</h1>
        ${listing.location} - ${listing.user.company.name}<br/>
        ${listing.htmlSafeDesc() | n}
        <br />
        <br />
        <a id="approve_${listing.listing_id}" href="${request.route_path('mod_listing_approve')}?listing_id=${listing.listing_id}"><button type="button" class="btn btn-primary">Approve Listing</button></a>
        <a id="remove_${listing.listing_id}" href="${request.route_path('mod_listing_remove')}?listing_id=${listing.listing_id}"><button type="button" class="btn btn-danger">Remove Listing</button></a>
        <hr/>
        %endfor
    </div>
</div>

