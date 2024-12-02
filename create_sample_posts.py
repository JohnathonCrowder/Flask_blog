import os
import sys
from datetime import datetime, timedelta
from app import create_app, db
from app.models import User, Post, PostImage
import requests
import io
from PIL import Image
from urllib.parse import urlparse
import random

# Unsplash API configuration
UNSPLASH_ACCESS_KEY = 'L_VjkkHKz79KRlp6ygxM3liNo7dQUXgjUCltLmeCDvM'  # Replace with your Unsplash API key
IMAGE_KEYWORDS = {
    "Technology": ["programming", "computer", "coding", "technology"],
    "Web Development": ["web-development", "coding", "computer-code", "programming"],
    "Security": ["cybersecurity", "computer-security", "network-security"],
    "DevOps": ["server-room", "technology", "cloud-computing"],
    "Backend": ["server", "database", "coding"],
    "Database": ["database", "server", "technology"],
    "Cloud": ["cloud-computing", "server", "technology"],
    "Testing": ["computer-testing", "coding", "technology"],
    "Mobile Development": ["mobile-development", "app-development", "coding"],
    "Programming": ["programming", "coding", "computer-code"]
}

def get_random_image(category):
    """Fetch a random relevant image from Unsplash"""
    try:
        keywords = IMAGE_KEYWORDS.get(category, ["technology"])
        keyword = random.choice(keywords)
        
        # First attempt: Unsplash API
        if UNSPLASH_ACCESS_KEY != 'YOUR_UNSPLASH_ACCESS_KEY':
            response = requests.get(
                f"https://api.unsplash.com/photos/random",
                params={
                    "query": keyword,
                    "orientation": "landscape",
                },
                headers={
                    "Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"
                }
            )
            
            if response.status_code == 200:
                image_data = response.json()
                image_url = image_data["urls"]["regular"]
                image_response = requests.get(image_url)
                if image_response.status_code == 200:
                    return image_response.content, "image/jpeg"
        
        # Fallback: Lorem Picsum (no API key needed)
        width, height = 800, 600
        response = requests.get(f"https://picsum.photos/{width}/{height}")
        if response.status_code == 200:
            return response.content, "image/jpeg"
            
    except Exception as e:
        print(f"Error fetching image: {str(e)}")
    
    return None, None

def add_images_to_post(post, content_images_count=2):
    """Add featured image and content images to a post"""
    try:
        # Add featured image
        image_data, mimetype = get_random_image(post.category)
        if image_data:
            post.featured_image_data = image_data
            post.featured_image_mimetype = mimetype

        # Add content images
        for i in range(content_images_count):
            image_data, mimetype = get_random_image(post.category)
            if image_data:
                post_image = PostImage(
                    image_data=image_data,
                    image_mimetype=mimetype,
                    caption=f"Illustration {i+1} for {post.title}",
                    position=i
                )
                post.images.append(post_image)

    except Exception as e:
        print(f"Error adding images to post: {str(e)}")

# Generate content for additional posts
def generate_post_content(title, category):
    return f"""
<h2>Introduction to {title}</h2>
<p>This comprehensive guide explores the key concepts and implementation details of {title}.</p>

<h3>Key Concepts</h3>
<ul>
    <li>Understanding the basics</li>
    <li>Implementation strategies</li>
    <li>Best practices</li>
    <li>Common pitfalls</li>
    <li>Advanced techniques</li>
</ul>

<h3>Example Implementation</h3>
<div class="code-block">
<pre><code>
// Example code for {category}
function example() {{
    console.log("Implementation details for {title}");
}}
</code></pre>
</div>

<h3>Best Practices</h3>
<ol>
    <li>Follow industry standards</li>
    <li>Implement proper error handling</li>
    <li>Write comprehensive tests</li>
    <li>Document your code</li>
</ol>

<h3>Advanced Topics</h3>
<ul>
    <li>Performance optimization</li>
    <li>Security considerations</li>
    <li>Scalability approaches</li>
    <li>Monitoring and maintenance</li>
</ul>

<h3>Common Challenges and Solutions</h3>
<p>When working with {title}, developers often face several challenges:</p>
<ul>
    <li>Integration complexity</li>
    <li>Performance bottlenecks</li>
    <li>Security vulnerabilities</li>
    <li>Maintenance overhead</li>
</ul>

<h3>Future Considerations</h3>
<p>As technology evolves, consider these upcoming trends:</p>
<ul>
    <li>Emerging standards</li>
    <li>New tools and frameworks</li>
    <li>Industry best practices</li>
    <li>Community developments</li>
</ul>
"""

# Define additional posts
ADDITIONAL_POSTS = [
    {
        "title": "CI/CD Pipeline Implementation with GitHub Actions",
        "subtitle": "Automating software delivery with GitHub Actions",
        "category": "DevOps",
        "tags": "ci-cd,github,automation,devops,deployment"
    },
    {
        "title": "Redis Caching Strategies for High-Performance Applications",
        "subtitle": "Implementing efficient caching with Redis",
        "category": "Backend",
        "tags": "redis,caching,performance,backend,databases"
    },
    {
        "title": "Vue.js 3 Composition API Deep Dive",
        "subtitle": "Understanding and implementing Vue 3's Composition API",
        "category": "Web Development",
        "tags": "vue,javascript,frontend,web-development,composition-api"
    },
    {
        "title": "Serverless Computing with AWS Lambda",
        "subtitle": "Building scalable applications with serverless architecture",
        "category": "Cloud",
        "tags": "aws,serverless,lambda,cloud,backend"
    },
    {
        "title": "Understanding OAuth 2.0 and OpenID Connect",
        "subtitle": "Implementing secure authentication and authorization",
        "category": "Security",
        "tags": "oauth,security,authentication,api,web-security"
    },
    {
        "title": "Building Real-Time Applications with WebSockets",
        "subtitle": "Implementing real-time features in web applications",
        "category": "Web Development",
        "tags": "websockets,real-time,javascript,backend,frontend"
    },
    {
        "title": "Testing React Applications with Jest and React Testing Library",
        "subtitle": "Best practices for testing React components",
        "category": "Testing",
        "tags": "testing,react,jest,frontend,tdd"
    },
    {
        "title": "Database Indexing Strategies for PostgreSQL",
        "subtitle": "Optimizing database performance with proper indexing",
        "category": "Database",
        "tags": "postgresql,database,performance,optimization,backend"
    },
    {
        "title": "Introduction to Rust Programming Language",
        "subtitle": "Getting started with systems programming in Rust",
        "category": "Programming",
        "tags": "rust,systems-programming,programming,performance,safety"
    },
    {
        "title": "Building Mobile Apps with React Native",
        "subtitle": "Cross-platform mobile development with React Native",
        "category": "Mobile Development",
        "tags": "react-native,mobile,javascript,cross-platform,development"
    },
    {
        "title": "Advanced Git Workflows for Teams",
        "subtitle": "Mastering Git for collaborative development",
        "category": "DevOps",
        "tags": "git,version-control,collaboration,devops,development"
    },
    {
        "title": "Building RESTful APIs with Node.js and Express",
        "subtitle": "Creating scalable and maintainable APIs",
        "category": "Backend",
        "tags": "nodejs,express,api,backend,rest"
    },
    {
        "title": "Machine Learning Model Deployment with TensorFlow",
        "subtitle": "From development to production with TensorFlow",
        "category": "Technology",
        "tags": "machine-learning,tensorflow,deployment,ai,python"
    },
    {
        "title": "Advanced CSS: Modern Layout Techniques",
        "subtitle": "Mastering CSS Grid and Flexbox",
        "category": "Web Development",
        "tags": "css,frontend,web-development,layout,design"
    },
    {
        "title": "Blockchain Development with Solidity",
        "subtitle": "Building decentralized applications on Ethereum",
        "category": "Technology",
        "tags": "blockchain,ethereum,solidity,web3,cryptocurrency"
    }
]

# Add content to additional posts
for post in ADDITIONAL_POSTS:
    post["content"] = generate_post_content(post["title"], post["category"])

def create_sample_posts():
    """Create sample blog posts with an admin user and images"""
    try:
        app = create_app()
        with app.app_context():
            # Ensure we have an admin user
            admin = User.query.filter_by(is_admin=True).first()
            if not admin:
                admin = User(
                    username="admin",
                    email="admin@example.com",
                    is_admin=True
                )
                admin.set_password("adminpass123")
                db.session.add(admin)
                db.session.commit()
                print("Created admin user")

            # Create posts with different dates and images
            for i, post_data in enumerate(ADDITIONAL_POSTS):
                # Check if post already exists
                existing_post = Post.query.filter_by(title=post_data["title"]).first()
                if existing_post:
                    print(f"Post '{post_data['title']}' already exists, skipping...")
                    continue

                # Create post
                post = Post(
                    title=post_data["title"],
                    subtitle=post_data["subtitle"],
                    content=post_data["content"],
                    category=post_data["category"],
                    tags=post_data["tags"],
                    status="published",
                    author=admin,
                    created_at=datetime.utcnow() - timedelta(days=i)
                )

                # Add images to the post
                add_images_to_post(post)
                
                # Update content with actual image IDs
                if post.images:
                    content = post.content
                    if len(post.images) > 0:
                        content = content.replace('[ID1]', str(post.images[0].id))
                    if len(post.images) > 1:
                        content = content.replace('[ID2]', str(post.images[1].id))
                    post.content = content
                
                # Add image references to content
                image_references = """
                <div class="post-images">
                    <figure>
                        <img src="/blog/content-image/[ID1]" alt="Illustration 1" class="post-image">
                        <figcaption>Illustration 1</figcaption>
                    </figure>
                    <figure>
                        <img src="/blog/content-image/[ID2]" alt="Illustration 2" class="post-image">
                        <figcaption>Illustration 2</figcaption>
                    </figure>
                </div>
                """
                
                db.session.add(post)
                db.session.flush()  # Get post ID
                
                # Update content with actual image IDs
                if post.images:
                    updated_references = image_references.replace('[ID1]', str(post.images[0].id))
                    if len(post.images) > 1:
                        updated_references = updated_references.replace('[ID2]', str(post.images[1].id))
                    post.content = post.content + updated_references

                print(f"Created post with images: {post_data['title']}")

            db.session.commit()
            print("All sample posts created successfully with images!")

    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    create_sample_posts()