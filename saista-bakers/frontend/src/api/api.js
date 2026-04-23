import axios from 'axios';

const USER_SERVICE_URL = process.env.REACT_APP_USER_SERVICE_URL || 'http://localhost:5001';
const ORDER_SERVICE_URL = process.env.REACT_APP_ORDER_SERVICE_URL || 'http://localhost:5002';

// Get auth token from localStorage
const getAuthToken = () => {
  return localStorage.getItem('authToken');
};

// User Service API calls
export const userAPI = {
  signup: async (username, email, password, fullName) => {
    try {
      const response = await axios.post(`${USER_SERVICE_URL}/signup`, {
        username,
        email,
        password,
        full_name: fullName
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  login: async (username, password) => {
    try {
      const response = await axios.post(`${USER_SERVICE_URL}/login`, {
        username,
        password
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  getProfile: async () => {
    try {
      const response = await axios.get(`${USER_SERVICE_URL}/profile`, {
        headers: { Authorization: `Bearer ${getAuthToken()}` }
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  getProducts: async (category = null) => {
    try {
      const url = category
        ? `${USER_SERVICE_URL}/products?category=${category}`
        : `${USER_SERVICE_URL}/products`;
      const response = await axios.get(url);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  getCategories: async () => {
    try {
      const response = await axios.get(`${USER_SERVICE_URL}/products/categories`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  getProduct: async (productId) => {
    try {
      const response = await axios.get(`${USER_SERVICE_URL}/products/${productId}`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  }
};

// Order Service API calls
export const orderAPI = {
  addToCart: async (productId, quantity) => {
    try {
      const response = await axios.post(`${ORDER_SERVICE_URL}/cart`, {
        product_id: productId,
        quantity
      }, {
        headers: { Authorization: `Bearer ${getAuthToken()}` }
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  getCart: async (orderId) => {
    try {
      const response = await axios.get(`${ORDER_SERVICE_URL}/cart/${orderId}`, {
        headers: { Authorization: `Bearer ${getAuthToken()}` }
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  removeFromCart: async (orderId, itemId) => {
    try {
      const response = await axios.delete(
        `${ORDER_SERVICE_URL}/cart/${orderId}/item/${itemId}`,
        { headers: { Authorization: `Bearer ${getAuthToken()}` } }
      );
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  placeOrder: async (orderId, deliveryAddress, deliveryDate) => {
    try {
      const response = await axios.post(`${ORDER_SERVICE_URL}/order`, {
        order_id: orderId,
        delivery_address: deliveryAddress,
        delivery_date: deliveryDate
      }, {
        headers: { Authorization: `Bearer ${getAuthToken()}` }
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  createCustomCake: async (pound, flavour, description, deliveryDate) => {
    try {
      const response = await axios.post(`${ORDER_SERVICE_URL}/custom-cake`, {
        pound,
        flavour,
        description,
        delivery_date: deliveryDate
      }, {
        headers: { Authorization: `Bearer ${getAuthToken()}` }
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  getCustomCake: async (orderId) => {
    try {
      const response = await axios.get(`${ORDER_SERVICE_URL}/custom-cake/${orderId}`, {
        headers: { Authorization: `Bearer ${getAuthToken()}` }
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  getOrders: async () => {
    try {
      const response = await axios.get(`${ORDER_SERVICE_URL}/orders`, {
        headers: { Authorization: `Bearer ${getAuthToken()}` }
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  getCustomCakes: async () => {
    try {
      const response = await axios.get(`${ORDER_SERVICE_URL}/custom-cakes`, {
        headers: { Authorization: `Bearer ${getAuthToken()}` }
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  }
};
