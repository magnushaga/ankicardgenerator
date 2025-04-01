import { useState, useEffect } from 'react';

export const useAuth = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);

  useEffect(() => {
    const checkAuth = () => {
      const token = localStorage.getItem('access_token');
      const userInfo = localStorage.getItem('user_info');
      
      if (token && userInfo) {
        setIsAuthenticated(true);
        setUser(JSON.parse(userInfo));
      } else {
        setIsAuthenticated(false);
        setUser(null);
      }
    };

    checkAuth();
    // Set up an interval to check auth status every 5 minutes
    const interval = setInterval(checkAuth, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  const getAccessToken = () => {
    return localStorage.getItem('access_token');
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_info');
    setIsAuthenticated(false);
    setUser(null);
  };

  return {
    isAuthenticated,
    user,
    getAccessToken,
    logout
  };
}; 