# app.py

from datetime import timedelta
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from cachetools import TTLCache 


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)

# We use a cache for every 2 minutes
cache = TTLCache(maxsize=100, ttl=120)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    author = db.Column(db.String(80), nullable=False)
    published_date = db.Column(db.String(80), nullable=False)

@app.route('/books', methods=['GET']) # Get method to retrieve data
def get_books():
    if 'books' in cache:
        app.logger.info("Returning books from cache")
        return jsonify({'books':cache['books']}), 200
    
    books_list = Book.query.all()
    books = [{'id': book.id, 'title': book.title, 'author': book.author, 'published_date': book.published_date} for book in books_list]
    
    # we store the result in the cache
    cache['books'] = books
    
    app.logger.info("Returning books from the database")
    
    return jsonify({'books': books}), 200

# in other routes, we will need to invalidate the cache when a book is added, updated, or deleted

@app.route('/books', methods=['POST']) # POST Method to create new data entries
def add_book():
    data = request.json
    new_book = Book(title=data['title'], author=data['author'], published_date=data['published_date'])
    db.session.add(new_book)
    db.session.commit()
    cache.pop('books', None)  # Invalidate the cache
    
    return jsonify({'message': 'Book added', 'book': {'id': new_book.id, 'title': new_book.title, 'author': new_book.author, 'published_date': new_book.published_date}}), 201

@app.route('/books/<int:id>', methods=['GET'])
def get_book(id):
    book = Book.query.get(id)
    if book is None:
        return jsonify({'error': 'Book not found'}), 404
    
    cache.pop('books', None)  # Invalidate the cache
    
    return jsonify({'book': {'id': book.id, 'title': book.title, 'author': book.author, 'published_date': book.published_date}}), 200

@app.route('/books/<int:id>', methods=['PUT']) # PUT Method to update data
def update_book(id):
    book = Book.query.get(id)
    if book is None:
        return jsonify({'error': 'Book not found'}), 404
    data = request.json
    book.title = data['title']
    book.author = data['author']
    book.published_date = data['published_date']
    db.session.commit()
    
    cache.pop('books', None)  # Invalidate the cache
    
    return jsonify({'message': 'Book updated', 'book': {'id': book.id, 'title': book.title, 'author': book.author, 'published_date': book.published_date}}), 200

@app.route('/books/<int:id>', methods=['DELETE']) # Delete method to delete data
def delete_book(id):
    book = Book.query.get(id)
    if book is None:
        return jsonify({'error': 'Book not found'}), 404
    db.session.delete(book)
    db.session.commit()
    
    cache.pop('books', None)  # Invalidate the cache
    
    return jsonify({'message': 'Book deleted'}), 200

if __name__ == '__main__':
    app.run(debug=True)
