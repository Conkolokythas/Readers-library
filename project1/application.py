from flask import Flask, render_template, request, session, redirect, url_for
import datetime
import requests
from models import *
app = Flask(__name__)
app.config['SECRET_KEY'] = '093659'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'database'
db = SQLAlchemy(app)


@app.route("/")
def index():
    return render_template("index.html", title="Readers' library")


@app.route("/register")
def register():
    return render_template("register.html", title="Register")


@app.route("/process", methods=["POST"])
def process():
    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("psw")
    a = User.query.filter_by(username=username).first()
    if a:
        return render_template("index.html", valid=True, m=a.username)
    else:
        data = [username, email, password]
        u = User(username=username, email=email, password=password)
        db.session.add(u)
        db.session.commit()
        return render_template("process.html", title="success", data=data)


@app.route("/login")
def login():
    return render_template("login.html", title="Login")


@app.route("/check", methods=["POST"])
def check():
    username = request.form.get("username")
    password = request.form.get("psw")
    log = User.query.filter_by(username=username).first() and User.query.filter_by(password=password).first()
    db.session.commit()
    session['username'] = username
    if log:
        return redirect(url_for("main"))
    else:
        return render_template("login.html", valid=True)


@app.route("/logout")
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))


@app.route("/main")
def main():
    if "username" in session:
        user = session['username']
        return render_template("main.html", title="Main", data=user)
    else:
        return render_template("login.html")


@app.route("/results", methods=['POST'])
def results():
    if request.method == 'POST':
        b = request.form.get("book")
        results = Book.query.filter(Book.title.like("%" + b + "%")).all() or Book.query.filter(Book.isbn.like("%" + b + "%")).all() or Book.query.filter(Book.author.like("%" + b + "%")).all()
        db.session.commit()
        user = session['username']
        return render_template("results.html", data=results, user=user)


@app.route("/book/<book_t>")
def book(book_t):
    if "username" in session:
        b = Book.query.filter_by(title=book_t).first()
        session['book'] = b.title
        r = Review.query.filter_by(book=b.title).all()
        db.session.commit()
        res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "wEchipPb45buJdleclKFHA", "isbns": b.isbn}).json()
        b_rating = res['books'][0]['average_rating']
        return render_template("book.html", user=session['username'], title=b.title, id=b.id, author=b.author, year=b.year, isbn=b.isbn, reviews=r, gr_rating=b_rating)
    else:
        return render_template("login.html")


@app.route("/review/<r_user>/<int:r_id>")
def review(r_user, r_id):
    if "username" in session:
        Review.query.filter_by(user=r_user).first()
        b = Book.query.get(r_id)
        db.session.commit()
        return render_template("review.html", user=session['username'], book=b.title)
    else:
        return render_template("login.html")


@app.route("/submit", methods=['POST'])
def submit():
    if "username" in session:
     book = request.form.get("book")
     heading = request.form.get("heading")
     review = request.form.get("review")
     scale = request.form.get("scale")
     date = datetime.date.today()
     author = session['username']
     comment = Review(user=author, book=book, review=review, date=date, scale=scale, title=heading)
     db.session.add(comment)
     db.session.commit()
     r = [book, heading, date, author, review, scale]
     return render_template("submit.html", r=r)
    else:
        return render_template("login.html")


@app.route("/profile/<user_name>")
def profile(user_name):
    if "username" in session:
        u = User.query.filter_by(username=user_name).first()
        book = session['book']
        b = Book.query.filter_by(title=book).first()
        p = Review.query.filter_by(user=session['username']).all()
        return render_template("profile.html", user=u.username, title=b.title, author=b.author, year=b.year, post=p)
    else:
        return render_template("login.html")


if __name__ == "__main__":
    app.run(debug=True)
