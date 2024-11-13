import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';
import DOMPurify from 'dompurify'; // For sanitizing HTML content

function Blog() {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // For handling delete functionality
  const [deleteLoading, setDeleteLoading] = useState(false);
  const [deleteError, setDeleteError] = useState(null);

  useEffect(() => {
    fetchPosts();
  }, []);

  const fetchPosts = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/posts');
      setPosts(response.data);
      setLoading(false);
    } catch (err) {
      setError('Error fetching blog posts');
      setLoading(false);
    }
  };

  const handleDelete = async (postId) => {
    if (!window.confirm('Are you sure you want to delete this post?')) return;

    setDeleteLoading(true);
    setDeleteError(null);

    try {
      await axios.delete(`http://localhost:5000/api/posts/${postId}`);
      setPosts(posts.filter(post => post.id !== postId));
    } catch (err) {
      setDeleteError('Error deleting post');
    } finally {
      setDeleteLoading(false);
    }
  };

  // Function to format date
  const formatDate = (dateString) => {
    const options = { 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    };
    return new Date(dateString).toLocaleDateString(undefined, options);
  };

  // Function to create excerpt from content
  const createExcerpt = (content, maxLength = 150) => {
    // Remove HTML tags for excerpt
    const stripHtml = content.replace(/<[^>]+>/g, '');
    if (stripHtml.length <= maxLength) return stripHtml;
    return stripHtml.substring(0, maxLength) + '...';
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

  return (
    <div className="container my-5">
      {/* Header Section */}
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1 className="mb-0">Blog Posts</h1>
        <Link to="/create-post" className="btn btn-primary">
          <i className="bi bi-plus-lg"></i> Create New Post
        </Link>
      </div>

      {/* Delete Error Alert */}
      {deleteError && (
        <div className="alert alert-danger alert-dismissible fade show" role="alert">
          {deleteError}
          <button 
            type="button" 
            className="btn-close" 
            onClick={() => setDeleteError(null)}
          ></button>
        </div>
      )}

      {/* Blog Posts Grid */}
      <div className="row g-4">
        {posts.length === 0 ? (
          <div className="col-12">
            <div className="alert alert-info">
              No blog posts found. Be the first to create one!
            </div>
          </div>
        ) : (
          posts.map(post => (
            <div className="col-md-6 col-lg-4" key={post.id}>
              <div className="card h-100 shadow-sm">
                {/* Card Image */}
                {post.image_url && (
                  <div className="card-img-wrapper" style={{ height: '200px', overflow: 'hidden' }}>
                    <img
                      src={post.image_url}
                      className="card-img-top"
                      alt={post.title}
                      style={{ 
                        height: '100%',
                        objectFit: 'cover',
                        width: '100%'
                      }}
                      onError={(e) => {
                        e.target.src = 'https://via.placeholder.com/400x200?text=No+Image';
                      }}
                    />
                  </div>
                )}

                {/* Card Body */}
                <div className="card-body">
                  <h5 className="card-title">{post.title}</h5>
                  <h6 className="card-subtitle mb-2 text-muted">
                    <small>
                      By {post.author} • {formatDate(post.created_at)}
                    </small>
                  </h6>
                  <div className="card-text mb-3">
                    {createExcerpt(post.content)}
                  </div>
                </div>

                {/* Card Footer */}
                <div className="card-footer bg-transparent border-top-0">
                  <div className="d-flex justify-content-between align-items-center">
                    <Link 
                      to={`/blog/${post.id}`} 
                      className="btn btn-outline-primary btn-sm"
                    >
                      Read More
                    </Link>
                    <div className="btn-group">
                      <Link 
                        to={`/edit-post/${post.id}`}
                        className="btn btn-outline-secondary btn-sm"
                      >
                        Edit
                      </Link>
                      <button
                        className="btn btn-outline-danger btn-sm"
                        onClick={() => handleDelete(post.id)}
                        disabled={deleteLoading}
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Back to Top Button */}
      <button
        onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
        className="btn btn-primary position-fixed bottom-0 end-0 m-4"
        style={{ display: window.pageYOffset > 100 ? 'block' : 'none' }}
      >
        ↑ Top
      </button>
    </div>
  );
}

export default Blog;