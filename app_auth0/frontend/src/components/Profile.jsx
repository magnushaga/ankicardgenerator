import React, { useState, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";

function Profile() {
  const [userInfo, setUserInfo] = useState(null);
  const [tokens, setTokens] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [supabaseUser, setSupabaseUser] = useState(null);
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    const urlParams = new URLSearchParams(location.search);
    const code = urlParams.get("code");

    if (code) {
      // Only exchange code if we haven't already processed it
      const processedCode = sessionStorage.getItem("processed_code");
      if (code !== processedCode) {
        sessionStorage.setItem("processed_code", code);
        exchangeCodeForToken(code);
      }
      // Clean up the URL after processing the code
      navigate('/profile', { replace: true });
    }
  }, [location, navigate]);

  const clearAllData = () => {
    // Clear all stored data
    sessionStorage.removeItem("processed_code");
    sessionStorage.removeItem("access_token");
    sessionStorage.removeItem("id_token");
    localStorage.removeItem("user_info");
    localStorage.removeItem("tokens");
    localStorage.removeItem("supabase_user");
    setUserInfo(null);
    setTokens(null);
    setSupabaseUser(null);
    setError(null);
  };

  const handleLogin = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const response = await fetch("http://localhost:5001/login");
      const data = await response.json();
      
      if (data.auth_url) {
        window.location.href = data.auth_url;
      }
    } catch (error) {
      setError("Error starting login process");
      console.error("Error:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = async () => {
    try {
      setIsLoading(true);
      setError(null);

      // Clear local application data first
      clearAllData();

      // Call backend logout endpoint
      const response = await fetch('http://localhost:5001/logout', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          returnTo: 'http://localhost:5173'
        })
      });

      if (!response.ok) {
        throw new Error('Logout failed');
      }

      const data = await response.json();

      // Redirect to Auth0 logout URL (will only log out of Auth0, not Google)
      if (data.logout_url) {
        window.location.href = data.logout_url;
      }
    } catch (error) {
      setError('Error during logout');
      console.error('Logout error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const exchangeCodeForToken = async (code) => {
    try {
      setIsLoading(true);
      setError(null);
      const response = await fetch('http://localhost:5001/callback', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          code,
          redirect_uri: 'http://localhost:5173/profile',
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to exchange code for token');
      }

      const data = await response.json();
      
      // Store tokens and user info
      setTokens(data.tokens);
      setUserInfo(data.user);
      setSupabaseUser(data.supabase_user);
      
      // Store in storage
      sessionStorage.setItem('access_token', data.tokens.access_token);
      sessionStorage.setItem('id_token', data.tokens.id_token);
      localStorage.setItem('user_info', JSON.stringify(data.user));
      localStorage.setItem('tokens', JSON.stringify(data.tokens));
      localStorage.setItem('supabase_user', JSON.stringify(data.supabase_user));
      
    } catch (error) {
      console.error('Error:', error);
      setError(error.message);
      clearAllData();
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    const savedUserInfo = localStorage.getItem("user_info");
    const savedTokens = localStorage.getItem("tokens");
    const savedSupabaseUser = localStorage.getItem("supabase_user");
    if (savedUserInfo && savedTokens && savedSupabaseUser) {
      setUserInfo(JSON.parse(savedUserInfo));
      setTokens(JSON.parse(savedTokens));
      setSupabaseUser(JSON.parse(savedSupabaseUser));
    }
  }, []);

  const formatJWT = (token) => {
    if (!token) return null;
    const [header, payload, signature] = token.split('.');
    try {
      return {
        header: JSON.parse(atob(header)),
        payload: JSON.parse(atob(payload)),
        signature: signature
      };
    } catch (e) {
      return { raw: token };
    }
  };

  if (isLoading) {
    return <div>Loading...</div>;
  }

  return (
    <div style={{ 
      padding: '20px',
      maxWidth: '800px',
      margin: '0 auto',
      fontFamily: 'Arial, sans-serif'
    }}>
      {error && (
        <div style={{ color: 'red', marginBottom: '20px' }}>
          {error}
        </div>
      )}
      
      {userInfo ? (
        <div>
          {/* Profile Header */}
          <div style={{ 
            display: 'flex', 
            alignItems: 'center', 
            gap: '20px',
            marginBottom: '30px',
            padding: '20px',
            backgroundColor: '#f8f9fa',
            borderRadius: '10px'
          }}>
            {userInfo.picture && (
              <img 
                src={userInfo.picture} 
                alt="Profile" 
                style={{ 
                  width: '100px', 
                  height: '100px', 
                  borderRadius: '50%',
                  objectFit: 'cover',
                  border: '3px solid white',
                  boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
                }} 
              />
            )}
            <div>
              <h1 style={{ margin: '0 0 10px 0' }}>{userInfo.name}</h1>
              <p style={{ margin: '0', color: '#666' }}>{userInfo.email}</p>
            </div>
          </div>

          {/* User Info Section */}
          <div style={{ marginBottom: '20px' }}>
            <h2>User Information</h2>
            <pre style={{ 
              backgroundColor: '#f8f9fa',
              padding: '15px',
              borderRadius: '5px',
              overflow: 'auto',
              fontSize: '14px'
            }}>
              {JSON.stringify(userInfo, null, 2)}
            </pre>
          </div>

          {/* JWT Token Section */}
          {tokens && (
            <div style={{ marginBottom: '20px' }}>
              <h2>Token Information</h2>
              <pre style={{ 
                backgroundColor: '#f8f9fa',
                padding: '15px',
                borderRadius: '5px',
                overflow: 'auto',
                fontSize: '14px'
              }}>
                {JSON.stringify(tokens, null, 2)}
              </pre>
            </div>
          )}

          {supabaseUser && (
            <div style={{ marginBottom: '20px' }}>
              <h3>Supabase User Data:</h3>
              <pre style={{ 
                background: '#f5f5f5', 
                padding: '10px', 
                borderRadius: '5px',
                overflow: 'auto'
              }}>
                {JSON.stringify(supabaseUser, null, 2)}
              </pre>
            </div>
          )}

          <button 
            onClick={handleLogout}
            disabled={isLoading}
            style={{
              padding: '10px 20px',
              backgroundColor: '#dc3545',
              color: 'white',
              border: 'none',
              borderRadius: '5px',
              cursor: 'pointer',
              fontSize: '16px'
            }}
          >
            {isLoading ? 'Logging out...' : 'Logout'}
          </button>
        </div>
      ) : (
        <div style={{ textAlign: 'center', marginTop: '50px' }}>
          <button 
            onClick={handleLogin}
            disabled={isLoading}
            style={{
              padding: '12px 24px',
              backgroundColor: '#007bff',
              color: 'white',
              border: 'none',
              borderRadius: '5px',
              cursor: 'pointer',
              fontSize: '16px',
              boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
            }}
          >
            {isLoading ? 'Logging in...' : 'Login with Auth0'}
          </button>
        </div>
      )}
    </div>
  );
}

export default Profile; 