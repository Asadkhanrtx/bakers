import React from 'react';
import Navbar from '../components/Navbar';
import '../styles/gallery.css';

const Gallery = () => {
  const images = [
    { url: 'https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=600&q=80', title: 'Elegant Chocolate' },
    { url: 'https://images.unsplash.com/photo-1535141192574-5d4897c82536?w=600&q=80', title: 'Berry Bliss' },
    { url: 'https://images.unsplash.com/photo-1616541823729-00fe0aacd32c?w=600&q=80', title: 'Red Velvet Love' },
    { url: 'https://images.unsplash.com/photo-1558636508-e0969c9c786b?w=600&q=80', title: 'Vintage Vanilla' },
    { url: 'https://images.unsplash.com/photo-1621303837174-89787a7d4729?w=600&q=80', title: 'Cookies & Cream' },
    { url: 'https://images.unsplash.com/photo-1562440499-64c9a111f713?w=600&q=80', title: 'Festive KitKat' },
    { url: 'https://images.unsplash.com/photo-1559620192-032c4bc4674e?w=600&q=80', title: 'Caramel Crunch' },
    { url: 'https://images.unsplash.com/photo-1464349095431-e9a21285b5f3?w=600&q=80', title: 'Blueberry Dream' },
    { url: 'https://images.unsplash.com/photo-1571115177098-24ec42ed204d?w=600&q=80', title: 'Tropical Pineapple' },
  ];

  return (
    <div className="gallery-page">
      <Navbar />
      <div className="gallery-hero">
        <h1>Our Gallery</h1>
        <p>A glimpse into our world of sweet creations</p>
      </div>
      <main className="gallery-container">
        <div className="gallery-grid">
          {images.map((img, index) => (
            <div key={index} className="gallery-item">
              <img src={img.url} alt={img.title} />
              <div className="gallery-overlay">
                <span>{img.title}</span>
              </div>
            </div>
          ))}
        </div>
      </main>
    </div>
  );
};

export default Gallery;
