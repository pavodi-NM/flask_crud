# app.py

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    author = db.Column(db.String(80), nullable=False)
    published_date = db.Column(db.String(80), nullable=False)

@app.route('/books', methods=['GET'])
def get_books():
    books_list = Book.query.all()
    books = [{'id': book.id, 'title': book.title, 'author': book.author, 'published_date': book.published_date} for book in books_list]
    return jsonify({'books': books}), 200

@app.route('/books', methods=['POST'])
def add_book():
    data = request.json
    new_book = Book(title=data['title'], author=data['author'], published_date=data['published_date'])
    db.session.add(new_book)
    db.session.commit()
    return jsonify({'message': 'Book added', 'book': {'id': new_book.id, 'title': new_book.title, 'author': new_book.author, 'published_date': new_book.published_date}}), 201

@app.route('/books/<int:id>', methods=['GET'])
def get_book(id):
    book = Book.query.get(id)
    if book is None:
        return jsonify({'error': 'Book not found'}), 404
    return jsonify({'book': {'id': book.id, 'title': book.title, 'author': book.author, 'published_date': book.published_date}}), 200

@app.route('/books/<int:id>', methods=['PUT'])
def update_book(id):
    book = Book.query.get(id)
    if book is None:
        return jsonify({'error': 'Book not found'}), 404
    data = request.json
    book.title = data['title']
    book.author = data['author']
    book.published_date = data['published_date']
    db.session.commit()
    return jsonify({'message': 'Book updated', 'book': {'id': book.id, 'title': book.title, 'author': book.author, 'published_date': book.published_date}}), 200

@app.route('/books/<int:id>', methods=['DELETE'])
def delete_book(id):
    book = Book.query.get(id)
    if book is None:
        return jsonify({'error': 'Book not found'}), 404
    db.session.delete(book)
    db.session.commit()
    return jsonify({'message': 'Book deleted'}), 200

if __name__ == '__main__':
    app.run(debug=True)
