from buddyup.app import app
from buddyup import database
from buddyup.templating import render_template


@app.route('/group/profile/<int:group_id>')
def group_view(group_id):
    group_record = database.Group.query.get_or_404(group_id)
    return render_template('group_view.html',
                            group_record=group_record)


@app.route('/group/search')
def group_search():
    return render_template('group_search.html')


@app.route('/group/search_results', methods=['POST'])
def group_search_results():
    """
    TODO: Implement searching by:
    * group.cid
    * group.name?
    * group.id + event.gid
    Give render_template a pagination
    """
    return render_template('group_search_results.html',
                           pagination=pagination)
