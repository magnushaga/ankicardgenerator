import React, { useEffect, useState } from "react";
import { useLocation } from "react-router-dom";
import { Container, Typography, Avatar, Box, Button, CircularProgress } from "@mui/material";
import { styled } from "@mui/material/styles";

const StyledContainer = styled(Container)(({ theme }) => ({
  display: "flex",
  flexDirection: "column",
  alignItems: "center",
  justifyContent: "center",
  height: "100vh",
  textAlign: "center",
  padding: theme.spacing(3),
}));

const Profile = () => {
  const [user, setUser] = useState(null);
  const [tokenPayload, setTokenPayload] = useState(null);
  const [loading, setLoading] = useState(true);
  const location = useLocation();

  const userVisualDetails = async (token) => {
    try {
      const response = await fetch("http://localhost:5001/userinfo", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      
      if (response.ok) {
        const userData = await response.json();
        return { name: userData.name, picture: userData.picture, email: userData.email };
      }
      return { name: null, picture: null };
    } catch (error) {
      console.error("Error fetching user details:", error);
      return { name: null, picture: null };
    }
  };

  const extractPayloadFromToken = (token) => {
    try {
      const payloadBase64 = token.split('.')[1];
      return JSON.parse(atob(payloadBase64));
    } catch (error) {
      console.error("Error extracting payload:", error);
      return null;
    }
  };

  const fetchUserInfo = async (token) => {
    setLoading(true);
    const visualDetails = await userVisualDetails(token);
    const decodedPayload = extractPayloadFromToken(token);

    setUser(visualDetails);
    setTokenPayload(decodedPayload);
    setLoading(false);
  };

  const exchangeCodeForToken = async (code) => {
    try {
      console.log("Starting code exchange...");
      const response = await fetch("http://localhost:5001/callback", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          code,
          redirect_uri: "http://localhost:5173/profile",
        }),
        credentials: 'include'
      });

      console.log("Response status:", response.status);
      const data = await response.json();
      console.log("Response data:", data);

      if (response.ok) {
        const { access_token } = data;
        if (!access_token) {
          throw new Error("No access token received");
        }
        sessionStorage.setItem("access_token", access_token);
        await fetchUserInfo(access_token);
      } else {
        throw new Error(data.error || "Failed to exchange code for token");
      }
    } catch (error) {
      console.error("Error exchanging code:", error);
      // You might want to show this error to the user
    }
  };

  const handleLogout = () => {
    const domain = import.meta.env.VITE_AUTH0_DOMAIN;
    const clientId = import.meta.env.VITE_AUTH0_CLIENT_ID;
    const returnTo = "http://localhost:5173";

    sessionStorage.removeItem("access_token");
    window.location.href = `https://${domain}/v2/logout?client_id=${clientId}&returnTo=${returnTo}`;
  };

  const handleLogin = () => {
    const domain = import.meta.env.VITE_AUTH0_DOMAIN;
    const clientId = import.meta.env.VITE_AUTH0_CLIENT_ID;
    const redirectUri = encodeURIComponent("http://localhost:5173/profile");
    const audience = encodeURIComponent("http://localhost:5000/api");
    const scope = encodeURIComponent("openid profile email");

    const authUrl = `https://${domain}/authorize?`
      + `response_type=code`
      + `&client_id=${clientId}`
      + `&redirect_uri=${redirectUri}`
      + `&audience=${audience}`
      + `&scope=${scope}`;

    window.location.href = authUrl;
  };

  useEffect(() => {
    const urlParams = new URLSearchParams(location.search);
    const code = urlParams.get("code");

    if (code) {
      exchangeCodeForToken(code);
    } else {
      const token = sessionStorage.getItem("access_token");
      if (token) {
        fetchUserInfo(token);
      } else {
        setLoading(false);
      }
    }
  }, [location.search]);

  if (loading) {
    return (
      <StyledContainer>
        <CircularProgress />
      </StyledContainer>
    );
  }

  if (!user) {
    return (
      <StyledContainer>
        <Typography variant="h5" gutterBottom>
          Welcome to StudyQuant
        </Typography>
        <Button
          variant="contained"
          color="primary"
          onClick={handleLogin}
        >
          Log In
        </Button>
      </StyledContainer>
    );
  }

  return (
    <StyledContainer>
      <Avatar
        alt={user.name || "User"}
        src={user.picture}
        sx={{ width: 120, height: 120, mb: 2 }}
      />
      <Typography variant="h4" gutterBottom>
        Welcome, {user.name}!
      </Typography>
      <Typography variant="body1" gutterBottom>
        {user.email}
      </Typography>
      <Box mt={3}>
        <Button variant="contained" color="error" onClick={handleLogout}>
          Log Out
        </Button>
      </Box>
      {tokenPayload && (
        <Box mt={3}>
          <Typography variant="h6" gutterBottom>
            Token Information:
          </Typography>
          <pre style={{ textAlign: 'left' }}>
            {JSON.stringify(tokenPayload, null, 2)}
          </pre>
        </Box>
      )}
    </StyledContainer>
  );
};

export default Profile; 