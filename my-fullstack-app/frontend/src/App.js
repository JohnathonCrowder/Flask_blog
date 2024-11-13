import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Home from './pages/Home';
import Blog from './pages/Blog';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap/dist/js/bootstrap.bundle.min.js';
import CreatePost from './pages/CreatePost';
import BlogPost from './pages/BlogPost';



function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/blog" element={<Blog />} />
          <Route path="/create-post" element={<CreatePost />} />
          <Route path="/blog/:id" element={<BlogPost />} />

          {/* Add more routes as needed */}
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;