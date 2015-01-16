import os

'''
Descriptions:
    BUDDYUP_ENABLE_AUTHENTICATION - if True, then use CAS or mockcas for authentication else automatically login any user without a password.  Warning: only disable this for testing / development!
    BUDDYUP_ENABLE_ADMIN_ALL_USERS - if True, then any user can access the admin pages. WARNING: only enable this for testing / development!
    DOMAIN_NAME - a string representing the fully qualified domain name (FQDN) of the app when running in each environment.
'''

class Base:
    BUDDYUP_ENABLE_AUTHENTICATION = True  # TODO: Default to CAS? Is that right?
    BUDDYUP_ENABLE_ADMIN_ALL_USERS = False
    CAS_SERVER = os.environ.get('CAS_SERVER', 'https://sso.pdx.edu/cas')
    SECRET_KEY = 'foo'
    DEFAULT_EMAIL_FORMAT = "buddyupdev+{user}@gmail.com"
    BUDDYUP_REQUIRE_PHOTO = True

class Dev(Base):
    AUTHENTICATION_SCHEME = os.environ.get('AUTHENTICATION_SCHEME', 'google').lower()
    BUDDYUP_ENABLE_AUTHENTICATION = (AUTHENTICATION_SCHEME == "cas")
    BUDDYUP_ENABLE_ADMIN_ALL_USERS = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/buddyup.db'
    # MockCAS server for testing
    CAS_SERVER = os.environ.get('CAS_SERVER', 'http://localhost:8000')
    ADMIN_USER = 'mockuser'
    BUDDYUP_REQUIRE_PHOTO = False
    DEFAULT_EMAIL_FORMAT = "buddyupdev+{user}@gmail.com"
    DOMAIN_NAME = os.environ.get('DOMAIN_NAME', 'buddyup.herokuapp.com')

class Production(Base):
    DEFAULT_EMAIL_FORMAT = os.environ.get('EMAIL_FORMAT', '{user}@pdx.edu')
    DOMAIN_NAME = os.environ.get('DOMAIN_NAME', 'buddyup.herokuapp.com')
    # In production we're either going to use CAS or Google.
    AUTHENTICATION_SCHEME = os.environ.get('AUTHENTICATION_SCHEME', 'cas').lower()
    BUDDYUP_ENABLE_AUTHENTICATION = (AUTHENTICATION_SCHEME == "cas")

class Testing(Base):
    BUDDYUP_ENABLE_AUTHENTICATION = False
    BUDDYUP_ENABLE_ADMIN_ALL_USERS = True
    CAS_SERVER = 'http://ec2-54-201-89-140.us-west-2.compute.amazonaws.com:80'
    ADMIN_USER = 'mockuser'
    BUDDYUP_REQUIRE_PHOTO = False
    DEFAULT_EMAIL_FORMAT = "buddyupdev+{user}@gmail.com"
    DOMAIN_NAME = os.environ.get('DOMAIN_NAME', 'buddyup.herokuapp.com')
