/**
 * Shared authentication utilities
 */

// Cache duration for token verification (5 minutes)
const TOKEN_VERIFICATION_INTERVAL = 5 * 60 * 1000;

/**
 * Verify access token with the backend
 * @param {string} accessToken - The access token to verify
 * @param {boolean} [forceVerify=false] - Force verification with backend even if cached
 * @returns {Promise<{isValid: boolean, user: object|null, error: string|null}>}
 */
export const verifyToken = async (accessToken, forceVerify = false) => {
  if (!accessToken) {
    console.log('No access token provided for verification');
    return { isValid: false, user: null, error: 'No token provided' };
  }

  try {
    // Check if we've verified recently, skip cache check if forceVerify is true
    if (!forceVerify) {
      const lastVerification = localStorage.getItem('last_token_verification');
      if (lastVerification && (Date.now() - parseInt(lastVerification)) < TOKEN_VERIFICATION_INTERVAL) {
        console.log('Using cached token verification, timestamp:', new Date(parseInt(lastVerification)).toLocaleString());
        const userInfo = localStorage.getItem('user_info');
        return { 
          isValid: true, 
          user: userInfo ? JSON.parse(userInfo) : null, 
          error: null 
        };
      } else {
        console.log('Token needs verification, last verification:', lastVerification ? 
          new Date(parseInt(lastVerification)).toLocaleString() : 'never');
      }
    } else {
      console.log('Force verifying token with backend, bypassing cache');
    }

    // Verify with backend using fetch with timeout
    console.log('Verifying token with backend...');
    
    // Create a fetch request with timeout
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 8000); // 8 second timeout
    
    try {
      const response = await fetch('http://localhost:5001/userinfo', {
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json'
        },
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);

      if (!response.ok) {
        if (response.status === 401) {
          console.warn('Token expired or invalid');
          return { isValid: false, user: null, error: 'Token expired or invalid' };
        }
        console.warn('Token verification failed:', response.status, response.statusText);
        return { isValid: false, user: null, error: `Verification failed: ${response.statusText}` };
      }

      const data = await response.json();
      if (data.user) {
        // Update local storage
        localStorage.setItem('user_info', JSON.stringify(data.user));
        const now = Date.now().toString();
        localStorage.setItem('last_token_verification', now);
        console.log('Token verified successfully, timestamp set to:', new Date(parseInt(now)).toLocaleString());
        return { isValid: true, user: data.user, error: null };
      }

      return { isValid: false, user: null, error: 'No user data returned' };
    } catch (fetchError) {
      clearTimeout(timeoutId);
      if (fetchError.name === 'AbortError') {
        console.error('Token verification request timed out after 8 seconds');
        // Use cached data if available when timeout occurs
        const userInfo = localStorage.getItem('user_info');
        const cachedUser = userInfo ? JSON.parse(userInfo) : null;
        
        // Use any existing timestamp or create a new one
        const now = Date.now().toString();
        localStorage.setItem('last_token_verification', now);
        
        return { 
          isValid: !!cachedUser, 
          user: cachedUser, 
          error: 'Verification request timed out' 
        };
      }
      throw fetchError; // Re-throw for the outer catch
    }
  } catch (error) {
    console.error('Token verification error:', error);
    if (error.message.includes('authentication') || error.message.includes('token')) {
      return { isValid: false, user: null, error: error.message };
    }
    
    // For network errors, use cached data if available
    const userInfo = localStorage.getItem('user_info');
    const cachedUser = userInfo ? JSON.parse(userInfo) : null;
    
    if (cachedUser) {
      console.log('Using cached user info due to network error');
      // Set a fresh timestamp
      const now = Date.now().toString();
      localStorage.setItem('last_token_verification', now);
      return { isValid: true, user: cachedUser, error: 'Network error, using cached data' };
    }
    
    // No cached data available
    return { isValid: false, user: null, error: error.message };
  }
};

/**
 * Clears the authentication cache from localStorage
 */
export const clearAuthCache = () => {
  localStorage.removeItem('last_token_verification');
  console.log('Cleared token verification cache');
};

/**
 * Clears all authentication data from localStorage
 */
export const clearAuthData = () => {
  localStorage.removeItem('tokens');
  localStorage.removeItem('user_info');
  localStorage.removeItem('access_token');
  localStorage.removeItem('processed_codes');
  localStorage.removeItem('last_token_verification');
  console.log('Cleared all auth data from localStorage');
};

/**
 * Get user info from localStorage
 * @returns {object|null} User info or null if not found
 */
export const getUserInfo = () => {
  const userInfo = localStorage.getItem('user_info');
  return userInfo ? JSON.parse(userInfo) : null;
};

/**
 * Get access token from localStorage
 * @returns {string|null} Access token or null if not found
 */
export const getAccessToken = () => {
  return localStorage.getItem('access_token');
};

/**
 * Check if the user is authenticated
 * @returns {boolean} True if authenticated, false otherwise
 */
export const isAuthenticated = () => {
  return !!getAccessToken() && !!getUserInfo();
}; 