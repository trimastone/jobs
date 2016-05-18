<%inherit file="base.mako"/>

<div class="container">
    %if (listing.user.user_id == request.authenticated_userid) and listing.approved is not False:
    <div class="alert alert-success" role="alert"><b>Thank You!</b> Your listing has been added successfully.</div>
    %endif
    
    %if listing.approved is False:
    <div class="alert alert-danger" role="alert">This listing has been removed.</div>
    %elif listing.removal_reason is not None:
    <div class="alert alert-warning" role="alert">This listing is no longer available by request of the poster.</div>
    %elif listing.user.user_id == request.authenticated_userid:
     %if listing.approved is None:
    <div class="alert alert-info" role="alert"><b>Approval Needed</b> - This listing will starting showing on the Listings page after it has been approved.</div>
     %endif
     %if listing.user.email_validated is not True:
    <div class="alert alert-info" role="alert"><b>Validation Needed</b> - This listing will starting showing on the Listings page after your email is validated. You should receive a validation email soon.</div>
     %endif
    %else:
     %if listing.approved is None or listing.user.email_validated is not True:
    <div class="alert alert-info" role="alert"><b>Listing Pending</b> - This listing will starting showing on the Listings page soon.</div>
     %endif
    %endif

    %if (listing.approved is True and listing.removal_reason is None and listing.user.email_validated is True) or (listing.user.user_id == request.authenticated_userid):
    <div class="row">
        <div class="col-md-12">
            <h1>${listing.title}</h1>
        </div>
        <div class="col-md-8">
            <h3>${company.name}</h3>
            <br />
            ${listing.htmlSafeDesc() | n}
            <br />
            <br />
            %if listing.user.user_id == request.authenticated_userid:
            <a href="${request.route_path('editlisting', listing_id=listing.listing_id)}"><button type="button" class="btn btn-primary">Edit Listing</button></a>
            <a href="${request.route_path('removelisting', listing_id=listing.listing_id)}"><button type="button" class="btn btn-primary">Remove Listing</button></a>
            %endif
        </div>
        <div id="apply_botton" class="col-md-4">
            <h3>About ${company.name}</h3>
            %if company.size:
            <b>Company Size:</b> ${company.size}<br/><br/>
            %endif
            %if company.market:
            <b>Market:</b> ${company.shortMarket()}<br/><br/>
            %endif
            %if company.culture:
            <b>Culture:</b> ${company.shortCulture()}<br/><br/>
            %endif
            %if company.software_meth:
            <b>Development Methodology:</b> ${company.shortSoftwareMeth()}<br/><br/>
            %endif
            
            <a href="${request.route_path('showcompany', company_id=company.company_id)}"><button type="button" class="btn btn-primary">Learn more about ${company.name}</button></a><br/><br/>
            <a href="${request.route_path('apply', listing_id=listing.listing_id)}"><button type="button" class="btn btn-primary">Apply For This Job</button></a><br/><br/>
        </div>
    </div>
    %endif
</div>
