<%inherit file="base.mako"/>
<div class="container">
    <div class="row">
        %for application in application_list:
        <h1>${application.listing.title}</h1>
        ${application.email}
        <br/>
        ${application.resume}
        <br/>
        <br/>
        ${application.cover_letter}
        <br/>
        <br/>
        <a id="approve_${application.application_id}" href="${request.route_path('mod_application_approve')}?application_id=${application.application_id}">
            <button type="button" class="btn btn-primary">Approve Application</button>
        </a>
        <a id="remove_${application.application_id}" href="${request.route_path('mod_application_remove')}?application_id=${application.application_id}">
            <button type="button" class="btn btn-danger">Remove Application</button>
        </a>
        <hr/>
        %endfor
    </div>
</div>
