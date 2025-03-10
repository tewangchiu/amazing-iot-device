"""
Tests for authentication functionality
"""

def test_login_page(client):
    """Test that the login page loads correctly."""
    response = client.get('/auth/login')
    assert response.status_code == 200
    assert b'Login' in response.data
    assert b'Username' in response.data
    assert b'Password' in response.data

def test_login_success(client, auth):
    """Test successful login."""
    response = auth.login()
    # Should redirect to dashboard after login
    assert response.headers['Location'] == '/dashboard/'

def test_login_failed(client):
    """Test failed login."""
    response = client.post(
        '/auth/login',
        data={'username': 'wrong_user', 'password': 'wrong_password'}
    )
    assert b'Invalid username or password' in response.data

def test_logout(client, auth):
    """Test logout functionality."""
    auth.login()

    response = auth.logout()
    # Should redirect to login page after logout
    assert response.headers['Location'] == '/auth/login'

def test_login_required(client):
    """Test login required for protected pages."""
    response = client.get('/dashboard/')
    # Should redirect to login page
    assert response.headers['Location'].startswith('/auth/login')
