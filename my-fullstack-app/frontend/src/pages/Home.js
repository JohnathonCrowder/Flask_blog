import React from 'react';

function Home() {
  return (
    <div className="container my-5">
      <div className="row">
        <div className="col-12">
          <h1 className="text-center mb-4">Welcome to Our Website</h1>
          
          {/* Hero Section */}
          <div className="p-5 mb-4 bg-light rounded-3">
            <div className="container-fluid py-5">
              <h2 className="display-5 fw-bold">Featured Content</h2>
              <p className="col-md-8 fs-4">
                This is a simple hero unit, a simple jumbotron-style component for
                calling extra attention to featured content or information.
              </p>
              <button className="btn btn-primary btn-lg" type="button">
                Learn more
              </button>
            </div>
          </div>

          {/* Content Cards */}
          <div className="row row-cols-1 row-cols-md-3 g-4 mt-4">
            {[1, 2, 3].map((item) => (
              <div className="col" key={item}>
                <div className="card h-100">
                  <div className="card-body">
                    <h5 className="card-title">Card {item}</h5>
                    <p className="card-text">
                      This is a sample card with some content. You can replace
                      this with your actual content.
                    </p>
                    <button className="btn btn-outline-primary">Read More</button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default Home;