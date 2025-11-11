"""Test script to verify admin app setup and dependencies."""
import sys
import os

def test_imports():
    """Test that all required imports work."""
    print("🔍 Testing imports...")
    
    try:
        import streamlit
        print(f"✅ Streamlit {streamlit.__version__}")
    except ImportError as e:
        print(f"❌ Streamlit import failed: {e}")
        return False
    
    try:
        import pandas
        print(f"✅ Pandas {pandas.__version__}")
    except ImportError as e:
        print(f"❌ Pandas import failed: {e}")
        return False
    
    try:
        import sqlite3
        print(f"✅ SQLite3 available")
    except ImportError as e:
        print(f"❌ SQLite3 import failed: {e}")
        return False
    
    try:
        from sqlalchemy.ext.asyncio import AsyncSession
        print(f"✅ SQLAlchemy async available")
    except ImportError as e:
        print(f"❌ SQLAlchemy async import failed: {e}")
        return False
    
    try:
        from src.database import AsyncSessionLocal
        from src.models import Tournament, Team, Season, Venue
        print(f"✅ Database models imported")
    except ImportError as e:
        print(f"❌ Database models import failed: {e}")
        return False
    
    try:
        from src.services.tournament_generator import generate_tournament_structure
        print(f"✅ Tournament generator imported")
    except ImportError as e:
        print(f"❌ Tournament generator import failed: {e}")
        return False
    
    return True


def test_database():
    """Test database connection."""
    print("\n🔍 Testing database...")
    
    import sqlite3
    
    db_path = "scores.db"
    if not os.path.exists(db_path):
        print(f"⚠️  Database not found at {db_path}")
        print("   Run: alembic upgrade head")
        print("   Then: python -m src.scripts.seed_data")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get table count
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"✅ Database connected ({len(tables)} tables)")
        
        # Check key tables
        required_tables = ['seasons', 'teams', 'venues', 'tournaments', 'matches']
        for table in required_tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"   - {table}: {count} rows")
        
        conn.close()
        return True
    
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False


def test_admin_app_file():
    """Test that admin app file exists and is valid Python."""
    print("\n🔍 Testing admin app file...")
    
    if not os.path.exists("admin_app.py"):
        print("❌ admin_app.py not found")
        return False
    
    print("✅ admin_app.py exists")
    
    # Try to compile it
    try:
        with open("admin_app.py", "r") as f:
            code = f.read()
        compile(code, "admin_app.py", "exec")
        print("✅ admin_app.py is valid Python")
        return True
    except SyntaxError as e:
        print(f"❌ Syntax error in admin_app.py: {e}")
        return False


def test_fastapi_endpoint():
    """Test that FastAPI admin endpoint exists."""
    print("\n🔍 Testing FastAPI admin endpoint...")
    
    try:
        from src.routers.admin_streamlit import router
        print("✅ Admin router imported")
        
        # Check if route exists
        routes = [route.path for route in router.routes]
        if "/admin" in routes:
            print("✅ /admin endpoint registered")
            return True
        else:
            print("⚠️  /admin endpoint not found in routes")
            return False
    
    except Exception as e:
        print(f"❌ FastAPI endpoint test failed: {e}")
        return False


def test_startup_script():
    """Test that startup script exists and is executable."""
    print("\n🔍 Testing startup script...")
    
    if not os.path.exists("run_admin.sh"):
        print("❌ run_admin.sh not found")
        return False
    
    print("✅ run_admin.sh exists")
    
    if os.access("run_admin.sh", os.X_OK):
        print("✅ run_admin.sh is executable")
        return True
    else:
        print("⚠️  run_admin.sh is not executable")
        print("   Run: chmod +x run_admin.sh")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("🏆 Scores Server Admin App - Setup Test")
    print("=" * 60)
    
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("Database", test_database()))
    results.append(("Admin App File", test_admin_app_file()))
    results.append(("FastAPI Endpoint", test_fastapi_endpoint()))
    results.append(("Startup Script", test_startup_script()))
    
    print("\n" + "=" * 60)
    print("📊 Test Results")
    print("=" * 60)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {name}")
    
    all_passed = all(result[1] for result in results)
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 All tests passed! Admin app is ready to use.")
        print("\nTo start the admin app:")
        print("  ./run_admin.sh")
        print("\nOr:")
        print("  streamlit run admin_app.py")
        print("\nLogin credentials:")
        print("  Username: admin")
        print("  Password: admin123")
    else:
        print("⚠️  Some tests failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("  - Install dependencies: pip install -r requirements.txt")
        print("  - Create database: alembic upgrade head")
        print("  - Seed data: python -m src.scripts.seed_data")
        print("  - Make script executable: chmod +x run_admin.sh")
    print("=" * 60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())

