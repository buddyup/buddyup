'''
Descriptions:
    BUDDYUP_ENABLE_AUTHENTICATION - if True, then use CAS or mockcas for authentication else automatically login any user without a password.  Warning: only disable this for testing / development!
    BUDDYUP_ENABLE_ADMIN_ALL_USERS - if True, then any user can access the admin pages. WARNING: only enable this for testing / development!
'''

class Base:
    BUDDYUP_ENABLE_AUTHENTICATION = True
    BUDDYUP_ENABLE_ADMIN_ALL_USERS = False
    CAS_SERVER = 'https://sso.pdx.edu/cas'
    SECRET_KEY = 'foo'
    DEFAULT_EMAIL_FORMAT = "{user}@pdx.edu"


class Dev(Base):
    BUDDYUP_ENABLE_AUTHENTICATION = False
    BUDDYUP_ENABLE_ADMIN_ALL_USERS = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/buddyup.db'
    # MockCAS server for testing
    CAS_SERVER = 'http://localhost:8000'
    ADMIN_USER = 'mockuser'


class Testing(Base):
    BUDDYUP_ENABLE_AUTHENTICATION = False
    BUDDYUP_ENABLE_ADMIN_ALL_USERS = True
    CAS_SERVER = 'http://ec2-54-201-89-140.us-west-2.compute.amazonaws.com:80'
    ADMIN_USER = 'mockuser'


class Production(Base):
    pass
