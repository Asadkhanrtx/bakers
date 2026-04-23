import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { userAPI, orderAPI } from '../api/api';
import '../styles/products.css';

function Products() {
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [quantities, setQuantities] = useState({});
  const navigate = useNavigate();

  useEffect(() => {
    const authToken = localStorage.getItem('authToken');
    if (!authToken) {
      navigate('/login');
      return;
    }

    fetchCategories();
    fetchProducts();
  }, [selectedCategory, navigate]);

  const fetchCategories = async () => {
    try {
      const data = await userAPI.getCategories();
      setCategories(data.categories);
    } catch (err) {
      console.error('Error fetching categories:', err);
    }
  };

  const fetchProducts = async () => {
    try {
      setLoading(true);
      const data = await userAPI.getProducts(selectedCategory || null);
      setProducts(data.products);
      setError('');
    } catch (err) {
      setError('Error loading products');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleQuantityChange = (productId, quantity) => {
    setQuantities({
      ...quantities,
      [productId]: Math.max(1, parseInt(quantity) || 1)
    });
  };

  const handleAddToCart = async (productId) => {
    try {
      const quantity = quantities[productId] || 1;
      const response = await orderAPI.addToCart(productId, quantity);
      localStorage.setItem('cartOrderId', response.order_id);
      alert('Product added to cart!');
    } catch (err) {
      alert('Error adding to cart: ' + (err.error || err));
    }
  };

  return (
    <div className="products-page">
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

      <main className="products-container">
        <div className="category-filter">
          <h3>Categories</h3>
          <button
            className={selectedCategory === '' ? 'active' : ''}
            onClick={() => setSelectedCategory('')}
          >
            All
          </button>
          {categories.map(category => (
            <button
              key={category}
              className={selectedCategory === category ? 'active' : ''}
              onClick={() => setSelectedCategory(category)}
            >
              {category}
            </button>
          ))}
        </div>

        <div className="products-list">
          <h2>{selectedCategory ? `${selectedCategory}` : 'All Products'}</h2>
          {loading ? (
            <p>Loading products...</p>
          ) : error ? (
            <p className="error">{error}</p>
          ) : products.length === 0 ? (
            <p>No products found</p>
          ) : (
            <div className="products-grid">
              {products.map(product => (
                <div key={product.id} className="product-card">
                  <h3>{product.name}</h3>
                  <p className="description">{product.description}</p>
                  <p className="price">Rs. {product.price}</p>
                  <div className="quantity-selector">
                    <input
                      type="number"
                      min="1"
                      value={quantities[product.id] || 1}
                      onChange={(e) => handleQuantityChange(product.id, e.target.value)}
                    />
                  </div>
                  <button onClick={() => handleAddToCart(product.id)}>
                    Add to Cart
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

export default Products;
