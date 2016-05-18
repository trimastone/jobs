<%inherit file="base.mako"/>

<div class="container">
    <div class="row">
        <div class="col-md-12">
            %if sub_header is not UNDEFINED:
            <h2>${sub_header}</h2>
            <br/>
            %endif
            ${form | n}
        </div>
    </div>
</div>

<script type="text/javascript">
   deform.load()
</script>
