class Base:
    CAS_SERVER = 'https://sso.pdx.edu/cas'
    SECRET_KEY = 'foo'
    ADMIN_USER = 'bforrest'


class Dev(Base):
    SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/buddyup.db'
    # MockCAS server for testing
    CAS_SERVER = 'http://localhost:8000'


class Testing(Base):
    pass


class Production(Base):
    pass
