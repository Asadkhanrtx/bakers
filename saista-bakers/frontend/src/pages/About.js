import React from 'react';
import Navbar from '../components/Navbar';
import '../styles/about.css';

const About = () => {
  return (
    <div className="about-page">
      <Navbar />
      <div className="about-hero">
        <h1>Our Sweet Story</h1>
      </div>
      <main className="about-container">
        <section className="about-content">
          <div className="about-text">
            <h2>Handcrafting Joy Since 2024</h2>
            <p>
              At <strong>Saista Bakers</strong>, we believe that every celebration deserves a centerpiece that is as 
              extraordinary as the moment itself. What started as a small passion project in a home kitchen 
              has grown into a premier destination for those who seek the perfect blend of artistry and flavor.
            </p>
            <p>
              Our master bakers use only the finest ingredients—from premium Belgian chocolate to fresh, 
              hand-picked fruits—to ensure that every bite is a revelation. We don't just bake cakes; 
              we create memories.
            </p>
            <div className="stats-grid">
              <div className="stat-item">
                <h3>100%</h3>
                <p>Natural Ingredients</p>
              </div>
              <div className="stat-item">
                <h3>500+</h3>
                <p>Custom Designs</p>
              </div>
              <div className="stat-item">
                <h3>24/7</h3>
                <p>Happiness Delivered</p>
              </div>
            </div>
          </div>
          <div className="about-image">
             <img src="https://images.unsplash.com/photo-1556910103-1c02745aae4d?w=800&q=80" alt="Our Bakery" />
          </div>
        </section>

        <section className="values-section">
          <h2>Why Choose Us?</h2>
          <div className="values-grid">
            <div className="value-card">
              <span className="icon">🎨</span>
              <h3>Bespoke Artistry</h3>
              <p>Every custom cake is a unique masterpiece designed specifically for you.</p>
            </div>
            <div className="value-card">
              <span className="icon">🌿</span>
              <h3>Purest Ingredients</h3>
              <p>We never compromise on quality. No preservatives, just pure goodness.</p>
            </div>
            <div className="value-card">
              <span className="icon">🚚</span>
              <h3>Timely Delivery</h3>
              <p>Your treats will always arrive fresh and on time for your special moments.</p>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
};

export default About;
