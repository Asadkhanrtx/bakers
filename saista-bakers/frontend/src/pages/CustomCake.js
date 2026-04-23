import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { orderAPI } from '../api/api';
import '../styles/custom-cake.css';

function CustomCake() {
  const [pound, setPound] = useState(1);
  const [flavour, setFlavour] = useState('fruit');
  const [description, setDescription] = useState('');
  const [deliveryDate, setDeliveryDate] = useState('');
  const [estimatedPrice, setEstimatedPrice] = useState(0);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState('');
  const navigate = useNavigate();

  const calculatePrice = (p, f) => {
    const basePrice = 300; // 1 pound base
    const extraPoundPrice = 200; // per extra pound

    const flavourSurcharge = {
      'fruit': 100,
      'chocolate': 200,
      'fondant': 250
    };

    // Calculate base price
    let price = p <= 1 ? basePrice : basePrice + (p - 1) * extraPoundPrice;

    // Add flavour surcharge per pound
    const flavourCharge = (flavourSurcharge[f] || 0) * p;

    return price + flavourCharge;
  };

  const handlePoundChange = (e) => {
    const newPound = parseInt(e.target.value);
    setPound(newPound);
    setEstimatedPrice(calculatePrice(newPound, flavour));
  };

  const handleFlavourChange = (e) => {
    const newFlavour = e.target.value;
    setFlavour(newFlavour);
    setEstimatedPrice(calculatePrice(pound, newFlavour));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!description || !deliveryDate) {
      alert('Please fill in all fields');
      return;
    }

    try {
      setLoading(true);
      await orderAPI.createCustomCake(pound, flavour, description, deliveryDate);
      setSuccess('Custom cake order created successfully! Check your email for confirmation.');
      setTimeout(() => navigate('/custom-cakes'), 2000);
    } catch (err) {
      alert('Error creating order: ' + (err.error || err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="custom-cake-page">
      <header className="navbar">
        <h1>Saista Bakers</h1>
        <div className="nav-links">
          <a href="/products">Products</a>
          <a href="/custom-cake">Custom Cake</a>
          <a href="/cart">Cart</a>
          <a href="/orders">Orders</a>
          <button onClick={() => {
            localStorage.clear();
            navigate('/login');
          }}>Logout</button>
        </div>
      </header>

      <main className="custom-cake-container">
        <div className="custom-cake-card">
          <h2>Design Your Custom Cake</h2>
          
          {success && <div className="success-message">{success}</div>}

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>Weight (Pounds)</label>
              <select value={pound} onChange={handlePoundChange} required>
                {[1, 2, 3, 4, 5, 6, 7, 8].map(p => (
                  <option key={p} value={p}>{p} lb</option>
                ))}
              </select>
              <p className="info">Base: Rs. 300 for 1 lb, +Rs. 200 for each extra pound</p>
            </div>

            <div className="form-group">
              <label>Flavour</label>
              <select value={flavour} onChange={handleFlavourChange} required>
                <option value="fruit">Fruit (+Rs. 100/lb)</option>
                <option value="chocolate">Chocolate (+Rs. 200/lb)</option>
                <option value="fondant">Fondant (+Rs. 250/lb)</option>
              </select>
            </div>

            <div className="form-group">
              <label>Design Description</label>
              <textarea
                placeholder="Describe your cake design, colors, theme, etc."
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                required
              />
            </div>

            <div className="form-group">
              <label>Delivery Date</label>
              <input
                type="date"
                value={deliveryDate}
                onChange={(e) => setDeliveryDate(e.target.value)}
                required
              />
            </div>

            <div className="price-display">
              <h3>Estimated Price: Rs. {estimatedPrice}</h3>
              <p className="note">Final price may vary based on design.</p>
            </div>

            <button type="submit" disabled={loading} className="submit-btn">
              {loading ? 'Creating order...' : 'Place Order'}
            </button>
          </form>

          <div className="pricing-info">
            <h3>Pricing Breakdown</h3>
            <ul>
              <li>Base (1 lb): Rs. 300</li>
              <li>Each extra pound: +Rs. 200</li>
              <li>Fruit per pound: +Rs. 100</li>
              <li>Chocolate per pound: +Rs. 200</li>
              <li>Fondant per pound: +Rs. 250</li>
            </ul>
          </div>
        </div>
      </main>
    </div>
  );
}

export default CustomCake;
