<%inherit file="base.mako"/>
<div class="container">
    <div class="row">
        <div class="col-md-12">
            <h1>${heading}</h1>
            <br />
            %for message in messageList:
            <p>${message}</p>
            %endfor
        </div>
    </div>
</div>
