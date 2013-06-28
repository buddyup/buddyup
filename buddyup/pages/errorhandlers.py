from buddyup.app import app
from buddyup.templating import render_template

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', e=e), 404