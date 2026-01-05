from flask import redirect, url_for, request
from shopyo.api.module import ModuleHelp
from shopyo.api.html import notify_success
from modules.polls.models import Question, Option
from modules.polls.forms import PollForm
from init import db

mhelp = ModuleHelp(__file__, __name__)
globals()[mhelp.blueprint_str] = mhelp.blueprint
module_blueprint = globals()[mhelp.blueprint_str]

@module_blueprint.route("/")
def index():
    questions = Question.query.all()
    context = {"questions": questions}
    return mhelp.render("index.html", **context)

@module_blueprint.route("/create", methods=["GET", "POST"])
def create():
    form = PollForm()
    if form.validate_on_submit():
        question = Question(text=form.text.data)
        db.session.add(question)
        db.session.commit()
        
        opt1 = Option(text=form.option1.data, question_id=question.id)
        opt2 = Option(text=form.option2.data, question_id=question.id)
        db.session.add_all([opt1, opt2])
        db.session.commit()
        
        notify_success("Poll created!")
        return redirect(url_for("polls.index"))
    
    return mhelp.render("create.html", form=form)

@module_blueprint.route("/<int:question_id>/vote", methods=["POST"])
def vote(question_id):
    option_id = request.form.get("option_id")
    if option_id:
        option = Option.query.get_or_404(option_id)
        option.votes += 1
        db.session.commit()
        notify_success("Vote cast!")
    return redirect(url_for("polls.results", question_id=question_id))

@module_blueprint.route("/<int:question_id>/results")
def results(question_id):
    question = Question.query.get_or_404(question_id)
    return mhelp.render("results.html", question=question)