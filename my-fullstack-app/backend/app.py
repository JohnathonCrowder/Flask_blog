from flask import Flask, jsonify, request
from flask_cors import CORS
from config import Config
from models import db, BlogPost

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)
db.init_app(app)

# Create tables
with app.app_context():
    db.create_all()

# Routes for blog posts
@app.route('/api/posts', methods=['GET'])
def get_posts():
    posts = BlogPost.query.order_by(BlogPost.created_at.desc()).all()
    return jsonify([post.to_dict() for post in posts])

@app.route('/api/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    post = BlogPost.query.get_or_404(post_id)
    return jsonify(post.to_dict())

@app.route('/api/posts', methods=['POST'])
def create_post():
    data = request.json
    new_post = BlogPost(
        title=data['title'],
        content=data['content'],
        author=data['author'],
        image_url=data.get('image_url')
    )
    db.session.add(new_post)
    db.session.commit()
    return jsonify(new_post.to_dict()), 201

@app.route('/api/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    post = BlogPost.query.get_or_404(post_id)
    data = request.json
    
    post.title = data.get('title', post.title)
    post.content = data.get('content', post.content)
    post.author = data.get('author', post.author)
    post.image_url = data.get('image_url', post.image_url)
    
    db.session.commit()
    return jsonify(post.to_dict())

@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    post = BlogPost.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    return '', 204

if __name__ == '__main__':
    app.run(debug=True)