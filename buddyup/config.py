class Base:
    CAS_SERVER = 'https://sso.pdx.edu/cas'
    SECRET_KEY = 'foo'


class Dev(Base):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///'
    # MockCAS server
    CAS_SERVER = 'http://locahost:8000/'


class Testing(Base):
    pass


class Production(Base):
    pass