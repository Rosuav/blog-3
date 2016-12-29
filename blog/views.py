from flask import request, redirect, url_for, render_template, flash
from flask_login import login_user, login_required
from werkzeug.security import check_password_hash

from . import app
from .database import session, Entry, User


@app.route("/")
@app.route("/page/<int:page>")
def entries(page=1, limit=10):
    PAGINATE_BY = limit

    if(request.args.get('limit') and request.args.get('limit').isdigit()):
        limit = int(request.args.get('limit'))
        if(0 < limit < 99):
            PAGINATE_BY = limit

    #Zero Indexing
    page_index = page - 1
    count = session.query(Entry).count()

    start = page_index * PAGINATE_BY
    end = start + PAGINATE_BY

    total_pages = (count - 1)//PAGINATE_BY + 1
    has_next = page_index < total_pages - 1
    has_prev = page_index > 0

    entries = session.query(Entry)
    entries = entries.order_by(Entry.datetime.desc())
    entries = entries[start:end]

    return render_template("entries.html",
                           entries=entries,
                           has_next=has_next,
                           has_prev=has_prev,
                           page=page,
                           total_pages=total_pages,
                           limit=limit,)

@app.route("/entry/add", methods=["GET"])
@login_required
def add_entry_get():
    return render_template("add_entry.html")

@app.route("/entry/add", methods=["POST"])
@login_required
def add_entry_post():
    entry=Entry(
        title=request.form["title"],
        content=request.form["content"],
        )
    session.add(entry)
    session.commit()
    return redirect(url_for("entries"))

@app.route("/entry/<int:entry_id>")
@login_required
def entry(entry_id):
    # Without .first(), entry is just the query itself rather than the results
    entry = session.query(Entry).filter_by(id=entry_id).first()
    return render_template("view_entry.html", entry=entry)

@app.route("/entry/edit/<int:entry_id>", methods=["GET", "POST"])
@login_required
def edit_entry(entry_id):
    entry = session.query(Entry).filter_by(id=entry_id).first()
    if request.method == 'POST':
        entry.content = request.form['content']
        entry.title = request.form['title']
        session.commit()
        return render_template("view_entry.html", entry=entry)
    return render_template("edit_entry.html", entry=entry)

@app.route("/entry/delete/<int:entry_id>", methods=["GET","POST"])
@login_required
def delete_entry(entry_id):
    entry = session.query(Entry).filter_by(id=entry_id).first()
    if request.method == 'POST':
        session.delete(entry)
        session.commit()
        return redirect(url_for("entries"))
    return render_template("delete_entry.html", entry=entry)

@app.route("/login", methods=["GET"])
def login_get():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login_post():
    email = request.form["email"]
    password = request.form["password"]
    user = session.query(User).filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        flash("Incorrect username or password", "danger")
        return redirect(url_for("login_get"))

    login_user(user)
    return redirect(request.args.get('next') or url_for("entries"))