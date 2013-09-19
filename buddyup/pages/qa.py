from datetime import datetime

from flask import redirect, url_for, g, abort

from sqlalchemy import func

from buddyup.app import app
from buddyup.database import (db, Question, QuestionVote,
                              Answer, AnswerVote, Course)
from buddyup.forms import QuestionForm, AnswerForm
from buddyup.util import check_course_membership, login_required
from buddyup.templating import render_template


def calculate_score(post_record):
    # TODO: Find the way to do the question using the SQL sum() function
    return sum(vote.value for vote in post_record.votes.all())


@app.route('/qa/question/post', methods=('GET', 'POST'))
@login_required
def question_create():
    form = QuestionForm()
    if form.validate_on_submit():
        question = Question(course_id=form.course.data.id,
                            user_id=g.user.id,
                            title=form.title.data,
                            time=datetime.now(),
                            text=form.text.data)
        db.session.add(question)
        db.session.commit()
        return redirect(url_for('question_view',
                                question_id=question.id))
    return render_template('qa/create.html',
                           form=form)


@app.route('/qa/question/remove/<int:question_id>')
@login_required
def question_remove(question_id):
    question = Question.query.get(question_id)
    if question.user_id != g.user.id:
        abort(404)
    else:
        course = question.course
        question.answers.delete()
        db.session.delete(question)
        db.session.commit()
        return redirect(url_for('question_list_course', course_id=course.id))


def course_for_template(course_record):
    questions = []
    for question_record in course_record.questions.all():
        questions.append({
            'title': question_record.title,
            'text': question_record.text,
            'url': url_for('question_view',
                            question_id=question_record.id),
            'time': question_record.time,
            'user': question_record.user,
            })
    return {
            'questions': questions,
            'name': course_record.name,
            'url': url_for('question_list_course',
                           course_id=course_record.id)
            }


@app.route('/qa/')
@login_required
def question_list_all():
    courses = map(course_for_template, g.user.courses.all())
    return render_template('qa/list_all.html',
                           courses=courses)


@app.route('/qa/course/<int:course_id>')
@login_required
def question_list_course(course_id):
    check_course_membership(course_id)
    course = Course.query.get(course_id)
    course = course_for_template(Course.query.get(course_id))
    return render_template('qa/list_course.html',
                           course=course)


def post_for_template(record):
    vote = record.votes.filter_by(user_id=g.user.id).first()
    if vote is None:
        status = 'neutral'
    elif vote.value == 1:
        status = 'upvoted'
    elif vote.value == -1:
        status = 'downvoted'
    else:
        raise Exception("vote has the invalid value %i" % vote.value)
    return {
        'status': status,
        'html_id': record.html_id,
        'score': calculate_score(record),
        'text': record.text,
        }


@app.route('/qa/question/view/<int:question_id>', methods=('GET', 'POST'))
@login_required
def question_view(question_id, form=None):
    if form is None:
        form = AnswerForm()
    question_record = Question.query.get(question_id)
    question = post_for_template(question_record)

    answers = map(post_for_template, question_record.answers.all())
    return render_template('qa/view.html',
                           form=form,
                           question=question,
                           answers=answers,
                           course=question_record.course,
                           )


@app.route('/qa/answer/post', methods=['POST'])
@login_required
def answer_create():
    form = AnswerForm()
    if form.validate_on_submit():
        check_course_membership(form.question_id)
        answer = Answer(question_id=form.question_id,
                        user_id=g.user.id,
                        title=form.title,
                        text=form.text,
                        time=datetime.now())
        db.session.add(answer)
        db.session.commit()
        return redirect(url_for('question_view',
                                question_id=form.question_id))
    return question_view(form.question_id, form=form)


def answer_vote(answer_id, value):
    # Generic up/down vote function
    answer = Answer.query.get_or_404(answer_id)
    check_course_membership(answer.question.course_id)
    Answer.votes.filter_by(user_id=g.user.id).delete()
    vote = AnswerVote(answer_id=answer_id,
                      user_id=g.user.id,
                      value=value)
    db.session.add(vote)
    db.session.commit()
    # TODO: Useful return value
    return u""


@app.route('/qa/answer/upvote/<int:answer_id>')
@login_required
def answer_upvote(answer_id):
    return answer_vote(answer_id, 1)


@app.route('/qa/answer/downvote/<int:answer_id>')
@login_required
def answer_downvote(answer_id):
    return answer_vote(answer_id, -1)


@app.route('/qa/answer/unvote/<int:answer_id>')
@login_required
def answer_unvote(answer_id):
    answer = Answer.query.get_or_404(answer_id)
    check_course_membership(answer.question.course_id)
    Answer.votes.filter_by(user_id=g.user.id).delete()
    db.session.commit()
    # TODO: Useful return value
    return u""


def question_vote(question_id, value):
    question = Question.query.get_or_404(question_id)
    check_course_membership(question.course_id)
    question.votes.filter_by(user_id=g.user.id).delete()
    vote = QuestionVote(question_id=question_id,
                        user_id=g.user.id,
                        value=value)
    db.session.add(vote)
    db.session.commit()
    # TODO: Return something
    return u""
 

@app.route('/qa/question/upvote/<int:answer_id>')
@login_required
def question_upvote(question_id):
    return question_vote(question_id, 1)


@app.route('/qa/question/downvote/<int:answer_id>')
@login_required
def question_downvote(question_id):
    return question_vote(question_id, -1)
 

@app.route('/qa/question/downvote/<int:question_id>')
@login_required
def question_unvote(question_id):
    question = Question.query.get_or_404(question_id)
    check_course_membership(question.course_id)
    question.votes.filter_by(user_id=g.user.id).delete()
    db.session.commit()
    return u""
