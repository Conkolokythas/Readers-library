import csv
import os

from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://qmavfxyyageuqp:39c9ae65cedc38c272eb45923218ac0ab57b18095d2ee12c5859c14b483e6126@ec2-46-137-124-19.eu-west-1.compute.amazonaws.com:5432/d55p1326t98kv7'
db = SQLAlchemy(app)

class Book(db.Model):
    __tablename__ = "Book"
    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.String, nullable=False)
    title = db.Column(db.String, nullable=False)
    author = db.Column(db.String, nullable=False)
    year = db.Column(db.String, nullable=False)



def main():
    db.create_all()

    f = open("books.csv")
    reader = csv.reader(f)
    for isbn, title, author, year in reader:
        book = Book(isbn=isbn, title=title, author=author, year=year)
        db.session.add(book)
        print(f"Book with isbn {isbn} title {title} written by {author} year {year} added.")
        db.session.commit()


if __name__ == "__main__":
    with app.app_context():
        main()