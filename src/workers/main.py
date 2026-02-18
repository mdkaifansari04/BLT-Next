"""
OWASP BLT - Cloudflare Python Worker
Main API handler for dynamic features
"""

from js import Response, fetch, Headers
import json
from datetime import datetime

# ===================================
# Configuration
# ===================================
ALLOWED_ORIGINS = [
    'https://owasp-blt.github.io',
    'http://localhost:3000',
    'http://localhost:8000',
]

# ===================================
# CORS Helpers
# ===================================
def get_cors_headers(origin):
    """Generate CORS headers for the response"""
    if origin in ALLOWED_ORIGINS or origin.endswith('.github.io'):
        return {
            'Access-Control-Allow-Origin': origin,
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
            'Access-Control-Max-Age': '86400',
        }
    return {}

def create_response(data, status=200, origin=None):
    """Create a JSON response with CORS headers"""
    headers = {
        'Content-Type': 'application/json',
        **get_cors_headers(origin) if origin else {},
    }
    
    return Response.new(
        json.dumps(data),
        status=status,
        headers=Headers.new(headers)
    )

def handle_cors_preflight(origin):
    """Handle CORS preflight requests"""
    return Response.new(
        '',
        status=204,
        headers=Headers.new(get_cors_headers(origin))
    )

# ===================================
# Route Handlers
# ===================================

async def handle_stats(request):
    """Handle /api/stats endpoint"""
    # In production, this would fetch from a database
    # For now, return mock data
    stats = {
        'bugs_reported': 15234,
        'active_researchers': 3421,
        'rewards_distributed': '$248,500',
        'projects_protected': 892,
    }
    
    return create_response(stats, origin=request.headers.get('Origin'))

async def handle_auth_login(request):
    """Handle /api/auth/login endpoint"""
    try:
        body = await request.json()
        email = body.get('email')
        password = body.get('password')
        
        # In production, validate against database
        # For now, mock authentication
        if email and password:
            user = {
                'id': 1,
                'username': email.split('@')[0],
                'email': email,
            }
            
            # Generate a mock JWT token (in production, use proper JWT)
            token = f"mock_token_{email}_{datetime.now().timestamp()}"
            
            return create_response({
                'success': True,
                'token': token,
                'user': user,
            }, origin=request.headers.get('Origin'))
        
        return create_response({
            'success': False,
            'error': 'Invalid credentials'
        }, status=401, origin=request.headers.get('Origin'))
        
    except Exception as e:
        return create_response({
            'success': False,
            'error': str(e)
        }, status=400, origin=request.headers.get('Origin'))

async def handle_auth_signup(request):
    """Handle /api/auth/signup endpoint"""
    try:
        body = await request.json()
        username = body.get('username')
        email = body.get('email')
        password = body.get('password')
        
        # In production, validate and store in database
        # For now, mock signup
        if username and email and password:
            user = {
                'id': 1,
                'username': username,
                'email': email,
            }
            
            # Generate a mock JWT token
            token = f"mock_token_{email}_{datetime.now().timestamp()}"
            
            return create_response({
                'success': True,
                'token': token,
                'user': user,
            }, origin=request.headers.get('Origin'))
        
        return create_response({
            'success': False,
            'error': 'Invalid signup data'
        }, status=400, origin=request.headers.get('Origin'))
        
    except Exception as e:
        return create_response({
            'success': False,
            'error': str(e)
        }, status=400, origin=request.headers.get('Origin'))

async def handle_auth_me(request):
    """Handle /api/auth/me endpoint"""
    auth_header = request.headers.get('Authorization', '')
    
    if not auth_header.startswith('Bearer '):
        return create_response({
            'error': 'Unauthorized'
        }, status=401, origin=request.headers.get('Origin'))
    
    token = auth_header.replace('Bearer ', '')
    
    # In production, validate JWT and fetch user from database
    # For now, mock user extraction from token
    if token.startswith('mock_token_'):
        parts = token.split('_')
        if len(parts) >= 3:
            email = parts[2]
            user = {
                'id': 1,
                'username': email.split('@')[0] if '@' in email else 'user',
                'email': email,
            }
            return create_response({
                'user': user
            }, origin=request.headers.get('Origin'))
    
    return create_response({
        'error': 'Invalid token'
    }, status=401, origin=request.headers.get('Origin'))

async def handle_auth_logout(request):
    """Handle /api/auth/logout endpoint"""
    # In production, invalidate token in database
    return create_response({
        'success': True
    }, origin=request.headers.get('Origin'))

async def handle_bugs_list(request):
    """Handle /api/bugs endpoint"""
    # In production, fetch from database with pagination
    bugs = [
        {
            'id': 1,
            'title': 'SQL Injection in login form',
            'severity': 'critical',
            'status': 'open',
            'reporter': 'alice',
            'reward': 500,
        },
        {
            'id': 2,
            'title': 'XSS vulnerability in comments',
            'severity': 'high',
            'status': 'verified',
            'reporter': 'bob',
            'reward': 300,
        },
    ]
    
    return create_response({
        'bugs': bugs,
        'total': len(bugs),
    }, origin=request.headers.get('Origin'))

async def handle_leaderboard(request):
    """Handle /api/leaderboard endpoint"""
    # In production, fetch from database
    leaderboard = [
        {'rank': 1, 'username': 'alice', 'points': 2500, 'bugs': 45},
        {'rank': 2, 'username': 'bob', 'points': 2100, 'bugs': 38},
        {'rank': 3, 'username': 'charlie', 'points': 1800, 'bugs': 32},
    ]
    
    return create_response({
        'leaderboard': leaderboard
    }, origin=request.headers.get('Origin'))

# ===================================
# Router
# ===================================

ROUTES = {
    'GET': {
        '/api/stats': handle_stats,
        '/api/auth/me': handle_auth_me,
        '/api/bugs': handle_bugs_list,
        '/api/leaderboard': handle_leaderboard,
    },
    'POST': {
        '/api/auth/login': handle_auth_login,
        '/api/auth/signup': handle_auth_signup,
        '/api/auth/logout': handle_auth_logout,
    },
}

async def route_request(request):
    """Route the request to the appropriate handler"""
    method = request.method
    url = request.url
    path = url.split('?')[0]  # Remove query params
    
    # Handle CORS preflight
    if method == 'OPTIONS':
        return handle_cors_preflight(request.headers.get('Origin'))
    
    # Find and execute handler
    method_routes = ROUTES.get(method, {})
    handler = method_routes.get(path)
    
    if handler:
        return await handler(request)
    
    # 404 Not Found
    return create_response({
        'error': 'Not found'
    }, status=404, origin=request.headers.get('Origin'))

# ===================================
# Main Entry Point
# ===================================

async def on_fetch(request):
    """Main entry point for Cloudflare Worker"""
    try:
        return await route_request(request)
    except Exception as e:
        return create_response({
            'error': 'Internal server error',
            'message': str(e)
        }, status=500, origin=request.headers.get('Origin'))
