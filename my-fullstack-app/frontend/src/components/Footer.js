import React from 'react';

function Footer() {
  return (
    <footer className="bg-dark text-light py-4 mt-auto">
      <div className="container">
        <div className="row">
          <div className="col-md-4">
            <h5>About Us</h5>
            <p>A brief description of your company or website.</p>
          </div>
          <div className="col-md-4">
            <h5>Quick Links</h5>
            <ul className="list-unstyled">
              <li><a href="/" className="text-light">Home</a></li>
              <li><a href="/about" className="text-light">About</a></li>
              <li><a href="/contact" className="text-light">Contact</a></li>
            </ul>
          </div>
          <div className="col-md-4">
            <h5>Contact Info</h5>
            <p>Email: info@example.com<br />
            Phone: (123) 456-7890<br />
            Address: 123 Street Name, City, Country</p>
          </div>
        </div>
        <div className="text-center mt-3">
          <p>&copy; 2023 Your Website. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
}

export default Footer;