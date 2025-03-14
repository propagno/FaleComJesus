import React, { createContext, useContext, useState, useEffect } from 'react';
import jwt_decode from 'jwt-decode';
import api from '../services/api';

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [currentUser, setCurrentUser] = useState(null);
  const [accessToken, setAccessToken] = useState(localStorage.getItem('accessToken') || null);
  const [refreshToken, setRefreshToken] = useState(localStorage.getItem('refreshToken') || null);
  const [loading, setLoading] = useState(true);
  
  // Check if token is expired
  const isTokenExpired = (token) => {
    if (!token) return true;
    
    try {
      const decoded = jwt_decode(token);
      const currentTime = Date.now() / 1000;
      return decoded.exp < currentTime;
    } catch (error) {
      console.error('Error decoding token:', error);
      return true;
    }
  };
  
  // Get user info from token
  const getUserFromToken = (token) => {
    if (!token) return null;
    
    try {
      const decoded = jwt_decode(token);
      return { id: decoded.sub };
    } catch (error) {
      console.error('Error getting user from token:', error);
      return null;
    }
  };
  
  // Refresh the access token
  const refreshAccessToken = async () => {
    if (!refreshToken) return false;
    
    try {
      console.log('Refreshing token...');
      const response = await api.post('/api/v1/auth/refresh', {}, {
        headers: {
          'Authorization': `Bearer ${refreshToken}`
        }
      });
      
      const newAccessToken = response.data.access_token;
      console.log('New token received:', newAccessToken ? 'Yes' : 'No');
      setAccessToken(newAccessToken);
      localStorage.setItem('accessToken', newAccessToken);
      return true;
    } catch (error) {
      console.error('Erro ao renovar token:', error);
      logout();
      return false;
    }
  };
  
  // Login user
  const login = async (email, password) => {
    try {
      const response = await api.post('/api/v1/auth/login', { email, password });
      
      const { access_token, refresh_token, user } = response.data;
      
      setAccessToken(access_token);
      setRefreshToken(refresh_token);
      setCurrentUser(user);
      
      localStorage.setItem('accessToken', access_token);
      localStorage.setItem('refreshToken', refresh_token);
      
      return { success: true };
    } catch (error) {
      return {
        success: false,
        message: error.response?.data?.message || 'Login failed'
      };
    }
  };
  
  // Register user
  const register = async (userData) => {
    try {
      const response = await api.post('/api/v1/auth/register', userData);
      
      const { access_token, refresh_token, user } = response.data;
      
      setAccessToken(access_token);
      setRefreshToken(refresh_token);
      setCurrentUser(user);
      
      localStorage.setItem('accessToken', access_token);
      localStorage.setItem('refreshToken', refresh_token);
      
      return { success: true };
    } catch (error) {
      return {
        success: false,
        message: error.response?.data?.message || 'Registration failed'
      };
    }
  };
  
  // Logout user
  const logout = () => {
    setCurrentUser(null);
    setAccessToken(null);
    setRefreshToken(null);
    
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    
    // Call logout API (optional, as JWT is stateless)
    api.post('/api/v1/auth/logout').catch(() => {});
  };
  
  // Load user profile
  const loadUserProfile = async () => {
    if (!accessToken) return false;
    
    try {
      const response = await api.get('/api/v1/users/me', {
        headers: {
          'Authorization': `Bearer ${accessToken}`
        }
      });
      
      setCurrentUser(response.data);
      return true;
    } catch (error) {
      if (error.response?.status === 401) {
        // Token expired, try to refresh
        const refreshed = await refreshAccessToken();
        if (refreshed) {
          return loadUserProfile();
        }
      }
      return false;
    }
  };
  
  // Initialize auth state
  useEffect(() => {
    const initAuth = async () => {
      if (accessToken) {
        if (isTokenExpired(accessToken)) {
          const refreshed = await refreshAccessToken();
          if (!refreshed) {
            logout();
          } else {
            await loadUserProfile();
          }
        } else {
          await loadUserProfile();
        }
      }
      
      setLoading(false);
    };
    
    initAuth();
  }, []);
  
  // Set up axios interceptor for token refresh
  useEffect(() => {
    const requestInterceptor = api.interceptors.request.use(
      async (config) => {
        if (!accessToken) return config;
        
        if (isTokenExpired(accessToken)) {
          const refreshed = await refreshAccessToken();
          if (refreshed) {
            config.headers.Authorization = `Bearer ${accessToken}`;
          }
        } else {
          config.headers.Authorization = `Bearer ${accessToken}`;
        }
        
        return config;
      },
      (error) => Promise.reject(error)
    );
    
    return () => {
      api.interceptors.request.eject(requestInterceptor);
    };
  }, [accessToken]);
  
  const value = {
    currentUser,
    accessToken,
    refreshToken,
    loading,
    isAuthenticated: !!accessToken && !isTokenExpired(accessToken),
    login,
    register,
    logout,
    refreshAccessToken,
    loadUserProfile
  };
  
  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
}; 