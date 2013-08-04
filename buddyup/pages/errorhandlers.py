from buddyup.app import app
from buddyup.templating import render_template


@app.errorhandler(404)
def error_page(e):
    """
    Dispatch to {error code}.html
    """
    return render_template('%i.html' % e.code, e=e), e.code