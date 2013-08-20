#!/usr/bin/env python
"""
MockCAS: Mock CAS server for testing

See ./mockcas.py for arguments
"""

from urllib import unquote

from flask import Flask, request, redirect
from flask.ext.runner import Runner

app = Flask(__name__)
runner = Runner(app)

DEFAULTS = {
    'status': 'success',
    'failmsg': "FAIL!",
    'failcode': "FAIL",
    'username': "mockuser",
    'ticket': "faketicket"
}

config = DEFAULTS.copy()

LOGIN_REDIRECT = "{service}?ticket={ticket}"
def success(username):
    return """
<cas:serviceResponse xmlns:cas='http://www.yale.edu/tp/cas'>
    <cas:authenticationSuccess>
        <cas:user>{username}</cas:user>
            <cas:proxyGrantingTicket>PGTIOU-84678-8a9d...
        </cas:proxyGrantingTicket>
    </cas:authenticationSuccess>
</cas:serviceResponse>
""".format(username=username)

def fail(message, code=None):
    if code is None:
        code = message
    return """
<cas:serviceResponse xmlns:cas='http://www.yale.edu/tp/cas'>
    <cas:authenticationFailure code="{code}">
        {message}
    </cas:authenticationFailure>
</cas:serviceResponse>
""".format(code=code, message=message)


@app.route('/set/<key>')
def set_config(key):
    config[key] = request.args.get('value', DEFAULTS.get(key))
    return "Set {} to {}".format(key, config[key])


@app.route('/get/<key>')
def get_config(key):
    return config.get(key, "DNE")


@app.route('/login')
def login():
    service = unquote(request.args['service'])
    app.logger.info("logging into %s", service)
    url = LOGIN_REDIRECT.format(
        service=service,
        ticket=config['ticket'])
    app.logger.info("CAS redirect to " + url)
    return redirect(url)


@app.route('/serviceValidate')
def validate():
    if config['status'] == 'success':
        return success(config['username'])
    else:
        return fail(config['failmsg'], config['failcode'])


@app.route('/logout')
def logout():
    return redirect(request.args['url'])


if __name__ == '__main__':
    runner.run()