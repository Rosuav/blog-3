from flask import request, redirect, url_for, render_template, flash
from flask_login import login_user, login_required, current_user, logout_user
from werkzeug.security import check_password_hash

from . import app
from .database import session, Entry, User


@app.route("/")
@app.route("/page/<int:page>")
def entries(page=1):
    PAGINATE_DEFAULT = 10
    # Investigate TRY EXCEPT to handle limit
    # TODO: Solve for range
    try:
        limit = int(request.args.get('limit'))
        PAGINATE_BY = limit
    except Exception as e:
        # TODO log e
        PAGINATE_BY = PAGINATE_DEFAULT

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
                           limit=PAGINATE_BY,)

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
        author=current_user
        )
    session.add(entry)
    session.commit()
    return redirect(url_for("entries"))

@app.route("/entry/<int:entry_id>")
def entry(entry_id):
    # Without .first(), entry is just the query itself rather than the results
    entry = session.query(Entry).filter_by(id=entry_id).first()
    is_author = entry.author == current_user
    return render_template("view_entry.html", entry=entry, is_author=is_author)

#TODO utilize .get(), ie session.query(Entry).get(entry_id) as
#this will return NONE if no entry which we can then build logic
#around
@app.route("/entry/<int:entry_id>/edit", methods=["GET", "POST"])
@login_required
def edit_entry(entry_id):
    entry = session.query(Entry).filter_by(id=entry_id).first()
    if request.method == 'POST':
        entry.content = request.form['content']
        entry.title = request.form['title']
        session.commit()
        return redirect(url_for("entry", entry_id=entry.id))
    return render_template("edit_entry.html", entry=entry)

#NOTE: Common practice to render_template on GET and 
#redirect on POST
@app.route("/entry/<int:entry_id>/delete", methods=["GET","POST"])
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

@app.route("/logout")
def logout():
    logout_user()
    flash("You have successfully logged out", "info")
    return redirect(url_for("entries"))