<%inherit file="base.mako"/>
<div class="container">
    <form class="form-horizontal" action="" method="post">
        <input type="hidden" name="came_from" value="${came_from}"/>
        <div class="form-group">
            <label for="email" class="col-sm-2 control-label">Email:</label>
            <div class="col-sm-10">
                <input type="email" class="form-control" id="email" placeholder="Email" name="username" value="${email}">
            </div>
        </div>
        <div class="form-group">
            <label for="password" class="col-sm-2 control-label">Password:</label>
            <div class="col-sm-10">
                <input type="password" class="form-control" id="password" placeholder="" name="password">
            </div>
        </div>
        <div class="form-group">
            <div class="col-sm-offset-2 col-sm-10">
                <button type="submit" class="btn btn-primary">Login</button>
                <a href="${request.route_path('changepw_req')}"><button type="button" class="btn btn-info">Forgot Password?</button></a>
            </div>
        </div>
    </form>
</div>
