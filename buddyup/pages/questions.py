from flask import g, request, flash, redirect, url_for, session, abort
from datetime import datetime
import time

from buddyup.app import app
from buddyup.database import Question, Answer, Vote, db
from buddyup.templating import render_template
from buddyup.util import args_get, login_required, form_get, check_empty

@app.route('/forum/', defaults={'page': 1})
@app.route('/forum/page/<int:page>')
@login_required
def view_all_question(page):
    pagination = (Question.query.order_by(Question.time)
            .paginate(page, per_page=20, error_out=True))
    # TODO: display about 10 questions per page in chronological order.
    # Use pagination?
    return render_template('qa/question.html', pagination=pagination)


@app.route('/forum/<int:question_id>')
@login_required
def view_question(question_id):
    question = Question.query.get_or_404(question_id)
    answers = Answer.query.filter_by(question_id=question.id).order_by(Answer.time)
    return render_template('view_question.html', question=question,
                                        answers=answers)


@app.route('/forum/post', methods=['GET', 'POST'])
@login_required
def post_question():
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
        return redirect(url_for('view_question', question_id=question_id))

@app.route('/forum/edit/<int:question_id>', methods=['POST', 'GET'])
@login_required
def edit_quesion(question_id):
    question = Question.query.filter_by(id=question_id, user_id=g.user.id).first_or_404()
    
    if request.method == 'GET':
        return render_template('edit_question.html', question=question,
                has_errors=False)
    else:
        title = form_get('title')
        check_empty(title, "Title")
        text = form_get('text')
        check_empty(text, "Text")
        time = datetime.now()
        
        if get_flashed_message():
            return render_template('edit_quesion.html', question=question,
                    has_errors=True)
        
        question.title = title
        question.text = text
        question.time = time
        db.session.update(question)
        db.sesion.commit()

        return redirect(url_for('view_question', question_id=question.id))


@app.route('/forum/remove/<int:question_id>', methods=['POST'])
@login_required
def remove_question(question_id):
    question = Question.query.filter_by(id=question_id, user_id=g.user.id).first_or_404()
    question.delete()
        #TODO: delete its answers
    db.session.commit()
    return redirect(url_for('view_question'))
