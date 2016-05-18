import transaction

import jobs.lib.jobslib

def addUserGroup(user_id, group_name):
    jobs_lib = jobs.lib.jobslib.get_jobs_lib()
    with transaction.manager:
        jobs_lib.addUserGroup(user_id, group_name)

def createAndLogin(testapp, email, password, **kw):
    createUser(email, password, **kw)
    return login(testapp, email, password)

def createUser(email, password, **kw):
    jobs_lib = jobs.lib.jobslib.get_jobs_lib()
    with transaction.manager:
        user = jobs_lib.createUser(email, password=password, **kw)
        jobs_lib.flushChanges()
        user_id = user.user_id
    return user_id

def createAdminAndLogin(testapp, email, password):
    user_id = createUser(email, password)
    addUserGroup(user_id, 'admin')
    login(testapp, email, password)

def login(testapp, email, password):
    res = testapp.get('/login/', status=200)
    form = res.form
    form['username'] = email
    form['password'] = password
    return form.submit()

def createCompany(name, **kw):
    jobs_lib = jobs.lib.jobslib.get_jobs_lib()
    with transaction.manager:
        company = jobs_lib.createCompany(name, **kw)
        jobs_lib.flushChanges()
        company_id = company.company_id
    return company_id
