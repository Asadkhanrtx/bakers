import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { orderAPI } from '../api/api';
import '../styles/cart.css';

function Cart() {
  const [cartItems, setCartItems] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [deliveryAddress, setDeliveryAddress] = useState('');
  const [deliveryDate, setDeliveryDate] = useState('');
  const [placing, setPlacing] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const authToken = localStorage.getItem('authToken');
    if (!authToken) {
      navigate('/login');
      return;
    }

    fetchCart();
  }, [navigate]);

  const fetchCart = async () => {
    try {
      const cartOrderId = localStorage.getItem('cartOrderId');
      if (!cartOrderId) {
        setCartItems([]);
        setTotal(0);
        setLoading(false);
        return;
      }

      const data = await orderAPI.getCart(cartOrderId);
      setCartItems(data.items);
      setTotal(data.total);
    } catch (err) {
      console.error('Error fetching cart:', err);
      setCartItems([]);
    } finally {
      setLoading(false);
    }
  };

  const handleRemoveItem = async (itemId) => {
    try {
      const cartOrderId = localStorage.getItem('cartOrderId');
      await orderAPI.removeFromCart(cartOrderId, itemId);
      fetchCart();
    } catch (err) {
      alert('Error removing item');
    }
  };

  const handlePlaceOrder = async (e) => {
    e.preventDefault();

    if (!deliveryAddress || !deliveryDate) {
      alert('Please fill in all fields');
      return;
    }

    if (cartItems.length === 0) {
      alert('Cart is empty');
      return;
    }

    try {
      setPlacing(true);
      const cartOrderId = localStorage.getItem('cartOrderId');
      await orderAPI.placeOrder(cartOrderId, deliveryAddress, deliveryDate);
      alert('Order placed successfully! Check your email for confirmation.');
      localStorage.setItem('cartOrderId', '');
      navigate('/orders');
    } catch (err) {
      alert('Error placing order: ' + (err.error || err));
    } finally {
      setPlacing(false);
    }
  };

  return (
    <div className="cart-page">
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

      <main className="cart-container">
        <h2>Shopping Cart</h2>

        {loading ? (
          <p>Loading cart...</p>
        ) : cartItems.length === 0 ? (
          <p>Your cart is empty</p>
        ) : (
          <div className="cart-content">
            <div className="cart-items">
              {cartItems.map(item => (
                <div key={item.id} className="cart-item">
                  <h3>{item.name}</h3>
                  <p>Quantity: {item.quantity}</p>
                  <p>Price per unit: Rs. {item.price}</p>
                  <p className="item-total">Total: Rs. {item.item_total.toFixed(2)}</p>
                  <button onClick={() => handleRemoveItem(item.id)} className="remove-btn">
                    Remove
                  </button>
                </div>
              ))}
            </div>

            <div className="order-summary">
              <h3>Order Summary</h3>
              <p className="total">Total: Rs. {total.toFixed(2)}</p>

              <form onSubmit={handlePlaceOrder}>
                <textarea
                  placeholder="Delivery Address"
                  value={deliveryAddress}
                  onChange={(e) => setDeliveryAddress(e.target.value)}
                  required
                />
                <input
                  type="date"
                  value={deliveryDate}
                  onChange={(e) => setDeliveryDate(e.target.value)}
                  required
                />
                <button type="submit" disabled={placing}>
                  {placing ? 'Placing order...' : 'Place Order'}
                </button>
              </form>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default Cart;
