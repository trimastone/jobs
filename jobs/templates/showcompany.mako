<%inherit file="base.mako"/>

<div class="container">
    <div class="row">
        <div class="col-md-12">
            <h1>${company.name}</h1>
        </div>
        %if company.size:
        <div class="col-md-8">
            <h3>Company Size</h3>
            <p>${company.size}</p>
        </div>
        %endif
        %if company.market:
        <div class="col-md-8">
            <h3>Market</h3>
            <p>${company.market}</p>
        </div>
        %endif
        %if company.culture:
        <div class="col-md-8">
            <h3>Culture</h3>
            <p>${company.culture}</p>
        </div>
        %endif
        %if company.software_meth:
        <div class="col-md-8">
            <h3>Development Methodology</h3>
            <p>${company.software_meth}</p>
        </div>
        %endif
        
        %if user and user.company_id == company.company_id:
        <div class="col-md-12">
            <a href="${request.route_path('editcompany', company_id=company.company_id)}"><button type="button" class="btn btn-primary">Edit Company Info</button></a>
        </div>
        %endif
    </div>
</div>
