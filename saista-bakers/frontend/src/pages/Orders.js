import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { orderAPI } from '../api/api';
import '../styles/orders.css';

function Orders() {
  const [orders, setOrders] = useState([]);
  const [customCakes, setCustomCakes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('orders');
  const navigate = useNavigate();

  useEffect(() => {
    const authToken = localStorage.getItem('authToken');
    if (!authToken) {
      navigate('/login');
      return;
    }

    fetchOrders();
  }, [navigate]);

  const fetchOrders = async () => {
    try {
      setLoading(true);
      const [ordersData, cakesData] = await Promise.all([
        orderAPI.getOrders(),
        orderAPI.getCustomCakes()
      ]);
      setOrders(ordersData.orders);
      setCustomCakes(cakesData.custom_cakes);
    } catch (err) {
      console.error('Error fetching orders:', err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status) => {
    const colors = {
      'pending': '#ff9800',
      'confirmed': '#4caf50',
      'completed': '#2196f3',
      'cancelled': '#f44336'
    };
    return <span className="status-badge" style={{ backgroundColor: colors[status] || '#999' }}>{status}</span>;
  };

  return (
    <div className="orders-page">
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

      <main className="orders-container">
        <h2>My Orders</h2>

        <div className="tabs">
          <button
            className={activeTab === 'orders' ? 'active' : ''}
            onClick={() => setActiveTab('orders')}
          >
            Regular Orders
          </button>
          <button
            className={activeTab === 'custom' ? 'active' : ''}
            onClick={() => setActiveTab('custom')}
          >
            Custom Cakes
          </button>
        </div>

        {loading ? (
          <p>Loading orders...</p>
        ) : (
          <div className="orders-content">
            {activeTab === 'orders' ? (
              orders.length === 0 ? (
                <p>No orders yet</p>
              ) : (
                <div className="orders-list">
                  {orders.map(order => (
                    <div key={order.id} className="order-card">
                      <h3>Order #{order.id}</h3>
                      <div className="order-details">
                        <p><strong>Total:</strong> Rs. {order.total_price.toFixed(2)}</p>
                        <p><strong>Status:</strong> {getStatusBadge(order.status)}</p>
                        <p><strong>Delivery Date:</strong> {order.delivery_date}</p>
                        <p><strong>Ordered:</strong> {new Date(order.created_at).toLocaleDateString()}</p>
                      </div>
                    </div>
                  ))}
                </div>
              )
            ) : (
              customCakes.length === 0 ? (
                <p>No custom cake orders yet</p>
              ) : (
                <div className="orders-list">
                  {customCakes.map(cake => (
                    <div key={cake.id} className="order-card">
                      <h3>Custom Cake Order #{cake.id}</h3>
                      <div className="order-details">
                        <p><strong>Weight:</strong> {cake.pound} lb</p>
                        <p><strong>Flavour:</strong> {cake.flavour}</p>
                        <p><strong>Description:</strong> {cake.description}</p>
                        <p><strong>Estimated Price:</strong> Rs. {cake.estimated_price.toFixed(2)}</p>
                        {cake.final_price && <p><strong>Final Price:</strong> Rs. {cake.final_price.toFixed(2)}</p>}
                        <p><strong>Status:</strong> {getStatusBadge(cake.status)}</p>
                        <p><strong>Delivery Date:</strong> {cake.delivery_date}</p>
                        <p><strong>Ordered:</strong> {new Date(cake.created_at).toLocaleDateString()}</p>
                      </div>
                    </div>
                  ))}
                </div>
              )
            )}
          </div>
        )}
      </main>
    </div>
  );
}

export default Orders;
