import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { orderAPI } from '../api/api';
import Navbar from '../components/Navbar';
import '../styles/cart.css';

function Cart() {
  const [cartItems, setCartItems] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [deliveryAddress, setDeliveryAddress] = useState('');
  const [deliveryDate, setDeliveryDate] = useState('');
  const [placing, setPlacing] = useState(false);
  const [orderSuccess, setOrderSuccess] = useState(null);
  const [showConfirm, setShowConfirm] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    if (!localStorage.getItem('authToken')) { navigate('/login'); return; }
    fetchCart();
  }, []);

  const fetchCart = async () => {
    setLoading(true);
    try {
      const cartOrderId = localStorage.getItem('cartOrderId');
      if (!cartOrderId) { setCartItems([]); setTotal(0); setLoading(false); return; }
      const data = await orderAPI.getCart(cartOrderId);
      setCartItems(data.items || []);
      setTotal(data.total || 0);
    } catch (err) {
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
    } catch (err) { alert('Error removing item'); }
  };

  const handleProceedToCheckout = (e) => {
    e.preventDefault();
    if (!deliveryAddress.trim()) { alert('Please enter a delivery address'); return; }
    if (!deliveryDate) { alert('Please select a delivery date'); return; }
    if (cartItems.length === 0) { alert('Your cart is empty'); return; }
    setShowConfirm(true);
  };

  const handleConfirmOrder = async () => {
    try {
      setPlacing(true);
      const cartOrderId = localStorage.getItem('cartOrderId');
      const result = await orderAPI.placeOrder(cartOrderId, deliveryAddress, deliveryDate);
      localStorage.removeItem('cartOrderId');
      setOrderSuccess({
        orderId: result.order_id || cartOrderId,
        total: result.total_price || total,
        deliveryDate,
        deliveryAddress,
      });
      setShowConfirm(false);
    } catch (err) {
      alert('Error placing order: ' + (err.error || err.detail || 'Please try again'));
    } finally {
      setPlacing(false);
    }
  };

  // ─── Order Success Screen ────────────────────────────────────
  if (orderSuccess) {
    return (
      <div className="cart-page">
        <Navbar />
        <div className="order-success-screen">
          <div className="success-card">
            <div className="success-icon">🎉</div>
            <h2>Order Placed Successfully!</h2>
            <p className="success-sub">Thank you for your order. A confirmation will be sent to your email.</p>
            <div className="success-details">
              <div className="detail-row"><span>Order ID</span><strong>#{orderSuccess.orderId}</strong></div>
              <div className="detail-row"><span>Total</span><strong>Rs. {Number(orderSuccess.total).toFixed(2)}</strong></div>
              <div className="detail-row"><span>Delivery Date</span><strong>{orderSuccess.deliveryDate}</strong></div>
              <div className="detail-row"><span>Address</span><strong>{orderSuccess.deliveryAddress}</strong></div>
            </div>
            <div className="payment-note">
              <h3>💳 Payment Instructions</h3>
              <p>Payment details have been sent to your registered email. You can pay via:</p>
              <ul>
                <li>📱 EasyPaisa / JazzCash</li>
                <li>🏦 Bank Transfer</li>
                <li>💵 Cash on Delivery</li>
              </ul>
              <p className="note-small">Our team will contact you within 2 hours to confirm your order.</p>
            </div>
            <div className="success-actions">
              <button onClick={() => navigate('/orders')} className="btn-view-orders">View My Orders</button>
              <button onClick={() => navigate('/products')} className="btn-shop-more">Continue Shopping</button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // ─── Confirm Order Modal ─────────────────────────────────────
  const ConfirmModal = () => (
    <div className="modal-overlay" onClick={() => setShowConfirm(false)}>
      <div className="confirm-modal" onClick={e => e.stopPropagation()}>
        <h3>Confirm Your Order</h3>
        <div className="confirm-items">
          {cartItems.map(item => (
            <div key={item.id} className="confirm-item">
              <span>{item.name} × {item.quantity}</span>
              <span>Rs. {item.item_total.toFixed(2)}</span>
            </div>
          ))}
          <div className="confirm-total">
            <span>Total</span>
            <strong>Rs. {total.toFixed(2)}</strong>
          </div>
        </div>
        <div className="confirm-info">
          <p>📍 <strong>{deliveryAddress}</strong></p>
          <p>📅 Delivery: <strong>{deliveryDate}</strong></p>
        </div>
        <p className="confirm-note">Payment instructions will be sent to your email after confirmation.</p>
        <div className="confirm-actions">
          <button className="btn-cancel" onClick={() => setShowConfirm(false)}>← Go Back</button>
          <button className="btn-confirm" onClick={handleConfirmOrder} disabled={placing}>
            {placing ? 'Placing Order...' : '✓ Confirm & Place Order'}
          </button>
        </div>
      </div>
    </div>
  );

  return (
    <div className="cart-page">
      <Navbar />
      {showConfirm && <ConfirmModal />}

      <div className="cart-hero">
        <h1>Your Shopping Cart</h1>
        <p>{cartItems.length} item{cartItems.length !== 1 ? 's' : ''} in your cart</p>
      </div>

      <main className="cart-main">
        {loading ? (
          <div className="cart-loading"><div className="spinner" /><p>Loading your cart...</p></div>
        ) : cartItems.length === 0 ? (
          <div className="empty-cart">
            <div className="empty-icon">🛒</div>
            <h3>Your cart is empty</h3>
            <p>Looks like you haven't added any items yet.</p>
            <Link to="/products" className="btn-shop-now">Browse Products</Link>
          </div>
        ) : (
          <div className="cart-layout">
            {/* Cart Items */}
            <div className="cart-items-panel">
              <h3>Order Items</h3>
              {cartItems.map(item => (
                <div key={item.id} className="cart-item-card">
                  <div className="cart-item-info">
                    <h4>{item.name}</h4>
                    <p>Qty: {item.quantity} × Rs. {item.price}</p>
                  </div>
                  <div className="cart-item-right">
                    <span className="cart-item-total">Rs. {item.item_total.toFixed(2)}</span>
                    <button className="remove-btn" onClick={() => handleRemoveItem(item.id)}>✕</button>
                  </div>
                </div>
              ))}
            </div>

            {/* Order Summary + Checkout Form */}
            <div className="order-summary-panel">
              <h3>Order Summary</h3>
              <div className="summary-lines">
                {cartItems.map(item => (
                  <div key={item.id} className="summary-line">
                    <span>{item.name} ×{item.quantity}</span>
                    <span>Rs. {item.item_total.toFixed(2)}</span>
                  </div>
                ))}
              </div>
              <div className="summary-total">
                <span>Total</span>
                <strong>Rs. {total.toFixed(2)}</strong>
              </div>

              <form onSubmit={handleProceedToCheckout} className="checkout-form">
                <h3>Delivery Details</h3>
                <label>Delivery Address *</label>
                <textarea
                  placeholder="Street address, city, area..."
                  value={deliveryAddress}
                  onChange={e => setDeliveryAddress(e.target.value)}
                  required
                  rows={3}
                />
                <label>Delivery Date *</label>
                <input
                  type="date"
                  value={deliveryDate}
                  min={new Date().toISOString().split('T')[0]}
                  onChange={e => setDeliveryDate(e.target.value)}
                  required
                />
                <div className="payment-info-box">
                  <h4>💳 Payment</h4>
                  <p>Payment details will be sent to your email after order confirmation. We accept EasyPaisa, JazzCash, Bank Transfer, and Cash on Delivery.</p>
                </div>
                <button type="submit" className="checkout-btn">
                  Proceed to Confirm →
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
