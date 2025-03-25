import requests
import json
import os
import sys
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

AUTH_SERVER_URL = 'http://localhost:5001'
API_SERVER_URL = 'http://localhost:5000'

def test_signup():
    logger.info("Testing signup...")
    try:
        response = requests.post(
            f'{AUTH_SERVER_URL}/api/auth/signup',
            json={
                'email': 'test@example.com',
                'password': 'testpassword123',
                'username': 'testuser'
            }
        )
        logger.info(f"Status Code: {response.status_code}")
        logger.info(f"Response: {response.json()}")
        return response.cookies.get('access_token')
    except Exception as e:
        logger.error(f"Signup test failed: {str(e)}")
        return None

def test_login():
    logger.info("Testing login...")
    try:
        response = requests.post(
            f'{AUTH_SERVER_URL}/api/auth/login',
            json={
                'email': 'test@example.com',
                'password': 'testpassword123'
            }
        )
        logger.info(f"Status Code: {response.status_code}")
        logger.info(f"Response: {response.json()}")
        return response.cookies.get('access_token')
    except Exception as e:
        logger.error(f"Login test failed: {str(e)}")
        return None

def test_get_current_user(token):
    logger.info("Testing get current user...")
    try:
        response = requests.get(
            f'{AUTH_SERVER_URL}/api/auth/me',
            cookies={'access_token': token}
        )
        logger.info(f"Status Code: {response.status_code}")
        logger.info(f"Response: {response.json()}")
    except Exception as e:
        logger.error(f"Get current user test failed: {str(e)}")

def test_social_auth():
    logger.info("Testing social auth...")
    providers = ['google', 'github', 'facebook', 'twitter']
    for provider in providers:
        try:
            response = requests.get(f'{AUTH_SERVER_URL}/api/auth/social/{provider}')
            logger.info(f"\n{provider.upper()} Auth URL:")
            logger.info(f"Status Code: {response.status_code}")
            logger.info(f"Response: {response.json()}")
        except Exception as e:
            logger.error(f"Social auth test failed for {provider}: {str(e)}")

def test_logout(token):
    logger.info("Testing logout...")
    try:
        response = requests.post(
            f'{AUTH_SERVER_URL}/api/auth/logout',
            cookies={'access_token': token}
        )
        logger.info(f"Status Code: {response.status_code}")
        logger.info(f"Response: {response.json()}")
    except Exception as e:
        logger.error(f"Logout test failed: {str(e)}")

def main():
    logger.info("Starting authentication tests...")
    
    # Test signup
    token = test_signup()
    if not token:
        logger.error("Signup failed, stopping tests")
        return
    
    # Test login
    token = test_login()
    if not token:
        logger.error("Login failed, stopping tests")
        return
    
    # Test get current user
    test_get_current_user(token)
    
    # Test social auth
    test_social_auth()
    
    # Test logout
    test_logout(token)
    
    logger.info("Authentication tests completed!")

if __name__ == '__main__':
    main() 