from urllib2 import urlopen
from xml.etree import cElementTree as etree

import logging

from buddyup import app

VALIDATE_URL = "{host}/serviceValidate?service={service}&ticket={ticket}"

BAD_RESPONSE_LOG_LEVEL = logging.ERROR

@app.route('/login', methods=['POST', 'GET'])
def login():
    ticket = 
    status = validate(ticket)


@app.route('/logout')
def logout():
    


def validate(ticket):
    """
    Validate the given ticket against app.config['CAS_HOST'].
    
    
    TODO: Error handling
    """
    cas_host = app.config['CAS_HOST']
    service = request.base_url
    url = VALIDATE_URL.format(host=cas_host,
                              service=request.base_url,
                              ticket=ticket)
    try:
        req = urlopen(url)
        tree = etree.parse(req)
    except etree.ParseError:
        
    
    # TODO: Graceful error handling for malformed CAS responses
    failure_elem = tree.find('cas:authenticationFailure')
    if failure_elem is not None:
        return Failure(failure_elem.text)

    success_elem = tree.find('cas:authenticationSuccess')
    if success is not None:
        request.session['user'] = success_elem.find('user').text
    else:
        app.logger.log(BAD_RESPONSE_LOG_LEVEL, )