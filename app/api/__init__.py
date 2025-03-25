# This file makes the api directory a Python package 

from .routes import api_bp
from .authRoutes import auth_bp

__all__ = ['api_bp', 'auth_bp'] 