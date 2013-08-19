from flask import g, request, flash, redirect, url_for, session, abort
from datetime import datetime
import time

from buddyup.app import app
from buddyup.database import Question, Answer, Vote, db
from buddyup.templating import render_template
from buddyup.util import args_get, login_required, form_get, check_empty


def view_all_answer(question_id):
    question = Question.query.get_or_404(question_id)
    return question.answer.all()


@app.route('/forum/answer/<int:answer_id>')
def view_answer(answer_id):
    answer = Answer.query.get_or_404(answer_id)
    return render_template('view_answer.html', answer=answer)


@app.route('/forum/answer_question/<int:question_id>', methods = ['GET', 'POST'])
@login_required
def create_answer(question_id):
    if request.method == 'GET':
        return render_template('post_answer.html', has_errors=False)
    else:
        user = g.user_id
        title = form_get('title')
        check_empty(title, "Title")
        text = form_get('text')
        check_empty(text, "Text")
        time = datetime.now()

        if get_flashed_message():
            return render_template('post_answer.html', has_errors=True)

        new_answer_record = Answer(user_id=user.id, question_id=question_id,
                title=title, text=text, time=time)
        db.session.add(new_answer_record)
        db.session.commit()

        return redirect(url_for('view_question', question_id=question_id))


@app.route('/forum/answer/edit/<int:answer_id>', methods = ['GET', 'POST'])
@login_required
def edit_answer(answer_id):
    answer = Answer.query.filter_by(id==answer_id, user_id==g.user.id).first_or_404()

    if request.method == 'GET':
        return render_template('edit_answer.html', answer=answer,
                has_errors=False)
    else:
        title = form_get('title')
        check_empty(title, "Title")
        text = form_get('text')
        check_empty(text, "Text")
        time = datetime.now()

        if get_flashed_message():
            return render_template('edit_answer.html', answer=answer,
                    has_errors=True)

        answer.title = title
        answer.text = text
        answer.time = time
        db.session.update(answer)
        db.session.commit()

        return redirect(url_for('view_question', question_id=answer.question_id))


@app.route('/forum/answer/remove/<int:answer_id>', methods=['GET', 'POST'])
def remove_answer(answer_id):
    answer = Answer.query.filter_by(id==answer_id, user_id==g.user.id).first_or_404()
    answer.delete()
    #TODO: delete its votes
    db.session.commit()
    return redirect(url_for('view_question', question_id=answer.question_id))
