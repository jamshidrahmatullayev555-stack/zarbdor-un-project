#!/usr/bin/env python3
"""
Test script to verify API implementation
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

def test_imports():
    """Test that all modules can be imported"""
    try:
        from api.routes import router as user_router
        from api.admin_routes import router as admin_router
        from api.main import app
        print("✓ All modules imported successfully")
        return user_router, admin_router, app
    except Exception as e:
        print(f"✗ Import error: {e}")
        return None, None, None

def test_routes(user_router, admin_router, app):
    """Test route counts"""
    if not all([user_router, admin_router, app]):
        return False
    
    user_routes = [r for r in user_router.routes]
    admin_routes = [r for r in admin_router.routes]
    
    print(f"✓ User API routes: {len(user_routes)} endpoints")
    print(f"✓ Admin API routes: {len(admin_routes)} endpoints")
    print(f"✓ Total app routes: {len(app.routes)} endpoints")
    
    return True

def test_endpoints():
    """List all endpoints"""
    from api.main import app
    
    print("\n=== User API Endpoints ===")
    for route in app.routes:
        if hasattr(route, 'methods') and hasattr(route, 'path'):
            if '/api/admin' not in route.path and route.path.startswith('/api'):
                methods = ', '.join(route.methods)
                print(f"{methods:10} {route.path}")
    
    print("\n=== Admin API Endpoints ===")
    for route in app.routes:
        if hasattr(route, 'methods') and hasattr(route, 'path'):
            if '/api/admin' in route.path:
                methods = ', '.join(route.methods)
                print(f"{methods:10} {route.path}")
    
    return True

def main():
    print("=" * 60)
    print("ZarbdorUn E-commerce API - Test Script")
    print("=" * 60)
    
    user_router, admin_router, app = test_imports()
    if not user_router:
        print("\n✗ Tests failed!")
        return False
    
    test_routes(user_router, admin_router, app)
    test_endpoints()
    
    print("\n" + "=" * 60)
    print("✓ All tests passed!")
    print("=" * 60)
    print("\nTo start the API server, run:")
    print("  python -m api.main")
    print("  or")
    print("  uvicorn api.main:app --reload")
    print("\nAPI Documentation will be available at:")
    print("  http://localhost:8000/docs")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
