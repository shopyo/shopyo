Building a Polls App (Tutorial)
===============================

This tutorial walks you through creating a simple Polls application using vanilla Shopyo. You will learn how to create modules, define models, create forms, and handle views.

Polls Tutorial Prerequisites
----------------------------
1.  **Create a Project:**
    
    .. code-block:: bash

       mkdir polls_project
       cd polls_project
       shopyo new
       cd polls_project
       shopyo initialise

Polls Implementation
--------------------

1.  **Create the Polls Module:**
    Use the `shopyo startapp` command to create a new module named `polls`.

    .. code-block:: bash

       shopyo startapp polls

2.  **Define Models:**
    Open `modules/polls/models.py` and define the `Question` and `Option` models.

    .. code-block:: python

       from init import db
       from shopyo.api.models import PkModel

       class Question(PkModel):
           __tablename__ = "questions"
           text = db.Column(db.String(200), nullable=False)
           options = db.relationship("Option", backref="question", lazy=True, cascade="all, delete-orphan")

       class Option(PkModel):
           __tablename__ = "options"
           text = db.Column(db.String(100), nullable=False)
           votes = db.Column(db.Integer, default=0)
           question_id = db.Column(db.Integer, db.ForeignKey("questions.id"), nullable=False)

3.  **Define Forms:**
    Open `modules/polls/forms.py` and create a form for adding polls.

    .. code-block:: python

       from flask_wtf import FlaskForm
       from wtforms import StringField, SubmitField, FieldList, FormField
       from wtforms.validators import DataRequired

       class OptionForm(FlaskForm):
           text = StringField("Option", validators=[DataRequired()])

       class PollForm(FlaskForm):
           text = StringField("Question", validators=[DataRequired()])
           # For simplicity, we'll just add fields for 2 options in this tutorial version
           option1 = StringField("Option 1", validators=[DataRequired()])
           option2 = StringField("Option 2", validators=[DataRequired()])
           submit = SubmitField("Create Poll")

4.  **Create Views:**
    Open `modules/polls/view.py` and implement the logic.

    .. code-block:: python

       from flask import redirect, url_for, request, flash
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

5.  **Create Templates:**
    Create the following files in `modules/polls/templates/polls/`.

    **index.html**:

    .. code-block:: html

       {% extends "shopyo_base/main_base.html" %}
       {% block content %}
       <div class="container">
           <h2>Active Polls</h2>
           <a href="{{ url_for('polls.create') }}" class="btn btn-primary mb-3">Create Poll</a>
           <ul class="list-group">
               {% for question in questions %}
               <li class="list-group-item">
                   <a href="{{ url_for('polls.results', question_id=question.id) }}">{{ question.text }}</a>
                   <form action="{{ url_for('polls.vote', question_id=question.id) }}" method="post" class="mt-2">
                       <input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>
                       {% for option in question.options %}
                       <div class="form-check">
                           <input class="form-check-input" type="radio" name="option_id" value="{{ option.id }}" id="opt{{ option.id }}" required>
                           <label class="form-check-label" for="opt{{ option.id }}">
                               {{ option.text }}
                           </label>
                       </div>
                       {% endfor %}
                       <button type="submit" class="btn btn-sm btn-success mt-2">Vote</button>
                   </form>
               </li>
               {% endfor %}
           </ul>
       </div>
       {% endblock %}

    **create.html**:

    .. code-block:: html

       {% extends "shopyo_base/main_base.html" %}
       {% block content %}
       <div class="container">
           <h2>Create Poll</h2>
           <form method="POST">
               {{ form.hidden_tag() }}
               <div class="form-group">
                   {{ form.text.label }}
                   {{ form.text(class="form-control") }}
               </div>
               <div class="form-group">
                   {{ form.option1.label }}
                   {{ form.option1(class="form-control") }}
               </div>
               <div class="form-group">
                   {{ form.option2.label }}
                   {{ form.option2(class="form-control") }}
               </div>
               {{ form.submit(class="btn btn-primary") }}
           </form>
       </div>
       {% endblock %}

    **results.html**:

    .. code-block:: html

       {% extends "shopyo_base/main_base.html" %}
       {% block content %}
       <div class="container">
           <h2>Results: {{ question.text }}</h2>
           <ul class="list-group">
               {% for option in question.options %}
               <li class="list-group-item d-flex justify-content-between align-items-center">
                   {{ option.text }}
                   <span class="badge badge-primary badge-pill">{{ option.votes }} votes</span>
               </li>
               {% endfor %}
           </ul>
           <a href="{{ url_for('polls.index') }}" class="btn btn-secondary mt-3">Back</a>
       </div>
       {% endblock %}

6.  **Run Migrations:**
    
    .. code-block:: bash

       shopyo db migrate
       shopyo db upgrade

7.  **Run the App:**

    .. code-block:: bash

       flask run --debug

    Go to `http://localhost:5000/polls` to see your app in action.

Polls Demo Source Code
----------------------
You can view the source code at `shopyo/demo/polls_demo`.
