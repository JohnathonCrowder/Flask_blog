import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import DOMPurify from 'dompurify';

function BlogPost() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [post, setPost] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchPost();
  }, [id]);

  const fetchPost = async () => {
    try {
      const response = await axios.get(`http://localhost:5000/api/posts/${id}`);
      setPost(response.data);
      setLoading(false);
    } catch (err) {
      setError('Error fetching blog post');
      setLoading(false);
    }
  };

  if (loading) return (
    <div className="container mt-5">
      <div className="text-center">
        <div className="spinner-border" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
      </div>
    </div>
  );

  if (error) return (
    <div className="container mt-5">
      <div className="alert alert-danger" role="alert">
        {error}
      </div>
    </div>
  );

  if (!post) return (
    <div className="container mt-5">
      <div className="alert alert-warning" role="alert">
        Post not found
      </div>
    </div>
  );

  return (
    <div className="container my-5">
      {/* Navigation */}
      <div className="mb-4">
        <Link to="/blog" className="btn btn-outline-secondary">
          ← Back to Blog
        </Link>
      </div>

      {/* Article */}
      <article className="blog-post">
        <h1 className="mb-4">{post.title}</h1>
        
        <div className="meta-info mb-4">
          <span className="text-muted">
            By {post.author} • {new Date(post.created_at).toLocaleDateString()}
          </span>
        </div>

        {post.image_url && (
          <div className="featured-image mb-4">
            <img
              src={post.image_url}
              alt={post.title}
              className="img-fluid rounded"
              style={{ maxHeight: '400px', width: '100%', objectFit: 'cover' }}
            />
          </div>
        )}

        <div 
          className="blog-content"
          dangerouslySetInnerHTML={{ 
            __html: DOMPurify.sanitize(post.content) 
          }}
        />
      </article>

      {/* Actions */}
      <div className="mt-5 pt-3 border-top">
        <div className="d-flex justify-content-between">
          <Link to="/blog" className="btn btn-outline-secondary">
            ← Back to Blog
          </Link>
          <div>
            <Link 
              to={`/edit-post/${post.id}`} 
              className="btn btn-primary me-2"
            >
              Edit Post
            </Link>
            <button 
              className="btn btn-danger"
              onClick={() => {
                if (window.confirm('Are you sure you want to delete this post?')) {
                  // Handle delete
                }
              }}
            >
              Delete Post
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default BlogPost;