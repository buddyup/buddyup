class Base:
    CAS_SERVER = 'https://sso.pdx.edu/cas'
    SECRET_KEY = 'foo'
    DEFAULT_EMAIL_FORMAT = "{user}@pdx.edu"


class Dev(Base):
    SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/buddyup.db'
    # MockCAS server for testing
    CAS_SERVER = 'http://localhost:8000'
    ADMIN_USER = 'mockuser'


class Testing(Base):
    pass


class Production(Base):
    pass
