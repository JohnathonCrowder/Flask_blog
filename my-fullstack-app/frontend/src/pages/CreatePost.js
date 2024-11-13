import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import ReactQuill from 'react-quill';
import 'react-quill/dist/quill.snow.css';

function CreatePost() {
  const navigate = useNavigate();
  
  // Form state
  const [formData, setFormData] = useState({
    title: '',
    content: '',
    author: '',
    image_url: ''
  });
  
  // UI state
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [previewMode, setPreviewMode] = useState(false);

  // Rich text editor configuration
  const modules = {
    toolbar: [
      [{ 'header': [1, 2, 3, false] }],
      ['bold', 'italic', 'underline', 'strike', 'blockquote'],
      [{ 'list': 'ordered' }, { 'list': 'bullet' }, { 'indent': '-1' }, { 'indent': '+1' }],
      ['link', 'image'],
      ['clean'],
      [{ 'color': [] }, { 'background': [] }],
      [{ 'font': [] }],
      [{ 'align': [] }],
      ['code-block']
    ],
  };

  const formats = [
    'header',
    'bold', 'italic', 'underline', 'strike', 'blockquote',
    'list', 'bullet', 'indent',
    'link', 'image',
    'color', 'background', 'font', 'align',
    'code-block'
  ];

  // Handle regular input changes
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prevState => ({
      ...prevState,
      [name]: value
    }));
    // Clear error when user starts typing
    if (error) setError(null);
  };

  // Handle rich text editor changes
  const handleEditorChange = (content) => {
    setFormData(prevState => ({
      ...prevState,
      content: content
    }));
    if (error) setError(null);
  };

  // Form validation
  const validateForm = () => {
    if (!formData.title.trim()) {
      setError('Title is required');
      return false;
    }
    if (!formData.author.trim()) {
      setError('Author is required');
      return false;
    }
    if (!formData.content.trim()) {
      setError('Content is required');
      return false;
    }
    if (formData.image_url && !isValidUrl(formData.image_url)) {
      setError('Please enter a valid image URL');
      return false;
    }
    return true;
  };

  // URL validation helper
  const isValidUrl = (string) => {
    try {
      new URL(string);
      return true;
    } catch (_) {
      return false;
    }
  };

  // Form submission handler
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validate form
    if (!validateForm()) return;

    setIsLoading(true);
    setError(null);

    try {
      await axios.post('http://localhost:5000/api/posts', formData);
      navigate('/blog'); // Redirect to blog page after successful submission
    } catch (err) {
      setError(err.response?.data?.message || 'Error creating blog post. Please try again.');
      console.error('Error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  // Preview component
  const PreviewPost = () => (
    <div className="preview-container border rounded p-4">
      <h2>{formData.title}</h2>
      <p className="text-muted">By {formData.author}</p>
      {formData.image_url && (
        <img
          src={formData.image_url}
          alt="Preview"
          className="img-fluid mb-3"
          style={{ maxHeight: '300px' }}
        />
      )}
      <div dangerouslySetInnerHTML={{ __html: formData.content }} />
    </div>
  );

  return (
    <div className="container my-5">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1>Create New Blog Post</h1>
        <button
          className="btn btn-secondary"
          onClick={() => setPreviewMode(!previewMode)}
        >
          {previewMode ? 'Edit Mode' : 'Preview Mode'}
        </button>
      </div>

      {error && (
        <div className="alert alert-danger" role="alert">
          {error}
        </div>
      )}

      {previewMode ? (
        <PreviewPost />
      ) : (
        <form onSubmit={handleSubmit} className="create-post-form">
          {/* Title Input */}
          <div className="mb-3">
            <label htmlFor="title" className="form-label">Title *</label>
            <input
              type="text"
              className="form-control"
              id="title"
              name="title"
              value={formData.title}
              onChange={handleChange}
              placeholder="Enter post title"
              required
            />
          </div>

          {/* Author Input */}
          <div className="mb-3">
            <label htmlFor="author" className="form-label">Author *</label>
            <input
              type="text"
              className="form-control"
              id="author"
              name="author"
              value={formData.author}
              onChange={handleChange}
              placeholder="Enter author name"
              required
            />
          </div>

          {/* Image URL Input */}
          <div className="mb-3">
            <label htmlFor="image_url" className="form-label">Image URL</label>
            <input
              type="url"
              className="form-control"
              id="image_url"
              name="image_url"
              value={formData.image_url}
              onChange={handleChange}
              placeholder="Enter image URL"
            />
          </div>

          {/* Image Preview */}
          {formData.image_url && (
            <div className="mb-3">
              <label className="form-label">Image Preview</label>
              <div className="image-preview border rounded p-2">
                <img
                  src={formData.image_url}
                  alt="Preview"
                  className="img-fluid"
                  style={{ maxHeight: '200px' }}
                  onError={(e) => {
                    e.target.onerror = null;
                    setError('Invalid image URL. Please check the URL and try again.');
                  }}
                />
              </div>
            </div>
          )}

          {/* Rich Text Editor */}
          <div className="mb-3">
            <label htmlFor="content" className="form-label">Content *</label>
            <ReactQuill
              theme="snow"
              value={formData.content}
              onChange={handleEditorChange}
              modules={modules}
              formats={formats}
              style={{ height: '300px', marginBottom: '50px' }}
            />
          </div>

          {/* Submit Button */}
          <div className="mb-3 mt-5">
            <button
              type="submit"
              className="btn btn-primary"
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                  Creating Post...
                </>
              ) : (
                'Create Post'
              )}
            </button>
            <button
              type="button"
              className="btn btn-secondary ms-2"
              onClick={() => navigate('/blog')}
            >
              Cancel
            </button>
          </div>
        </form>
      )}
    </div>
  );
}

export default CreatePost;