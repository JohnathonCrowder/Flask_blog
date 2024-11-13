import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';


function Blog() {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

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

  if (loading) return <div className="container mt-5">Loading...</div>;
  if (error) return <div className="container mt-5 text-danger">{error}</div>;

  return (
    <div className="container my-5">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1>Blog Posts</h1>
        <Link to="/create-post" className="btn btn-primary">
          Create New Post
        </Link>
      </div>
      <div className="row">
        {posts.map(post => (
          <div className="col-md-6 mb-4" key={post.id}>
            <div className="card h-100">
              {post.image_url && (
                <img 
                  src={post.image_url} 
                  className="card-img-top" 
                  alt={post.title}
                  style={{ height: '200px', objectFit: 'cover' }}
                />
              )}
              <div className="card-body">
                <h5 className="card-title">{post.title}</h5>
                <h6 className="card-subtitle mb-2 text-muted">
                  By {post.author} on {new Date(post.created_at).toLocaleDateString()}
                </h6>
                <p className="card-text">
                  {post.content.substring(0, 150)}...
                </p>
                <button className="btn btn-primary">Read More</button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Blog;