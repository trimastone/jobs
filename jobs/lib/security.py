import hashlib

from jobs.lib.model import DBSession, User

def groupfinder(user_id, request):
    """Return a list of all the groups that the user with id user_id is in."""
    ret = DBSession.query(User).filter_by(user_id=user_id).all()
    if len(ret) == 0:
        return None
    user = ret[0]
    groups = [x.group_name for x in user.groups]
    return groups

def hashPassword(password, password_string):
    """Hash the given password for storage in the database."""
    d = hashlib.sha256()
    d.update(password_string + password)
    return d.hexdigest()
