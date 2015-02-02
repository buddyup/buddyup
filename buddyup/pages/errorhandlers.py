from buddyup.app import app
from buddyup.templating import render_template


@app.errorhandler(400)
@app.errorhandler(403)
@app.errorhandler(404)
@app.errorhandler(500)
@app.errorhandler(503)
def error_page(e):
    """
    Dispatch to {error code}.html
    """
    import traceback
    traceback.print_exc()
    return render_template('errors/%i.html' % e.code, e=e), e.code
