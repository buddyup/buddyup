from flask import g, request, flash, redirect, url_for, session, abort
from datetime import datetime
import time

from buddyup.app import app
from buddyup.database import Question, Answer, Vote, db
from buddyup.templating import render_template
from buddyup.util import args_get, login_required, form_get, check_empty

@app.route('/forum')
def question_view_all():
    # TODO: display about 10 questions per page in chronological order.
    # Use pagination?
    pass


@app.route('/forum/<int:question_id>')
def question_view(question_id):
    question = Question.query.get_or_404(question_id)
    answers = Answer.query.filter_by(question_id=question.id).order_by(Answer.time)
    return render_template('view_question.html', question=question,
                                        answers=answers)


@app.route('/forum/post_question', methods=['GET', 'POST'])
@login_required
def question_create():
    if request.method == 'GET':
        return render_template('post_question.html', has_errors=False)
    else:
        user = g.user
        title = form_get('title')
        check_empty(title, "Title")
        text = form_get('content')
        check_empty(text, "Content")
        time = datetime.now()

        if get_flashed_message():
            return render_template('post_question.html', has_errors=True)
        
        new_question_record = Question(user_id=user.id, title=title,
                                text=text, time=time)
        db.session.add(new_question_record)
        db.session.commit()
        #TODO: refer to event_create
        #question_id = Question.query.filter_
        return redirect(url_for('question_view', question_id=question_id))

@app.route('/forum/remove/<int:question:id>', methods = ['POST'])
@login_required
def question_remove(question_id):
    question = Question.query.filter_by(id=question_id, user_id=g.user.id)

    if question is None:
        abort(403)
    else:
        question.first().delete()
        db.session.commit()
        return redirect(url_for('question_view'))
