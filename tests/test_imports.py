def test_imports():
    """Simple tests to verify that we can import app modules"""
    try:
        from main import app
        assert app is not None, "App should be importable"
        print("Successfully imported app")
    except ImportError as e:
        print(f"Import error: {e}")
        assert False, f"Failed to import app: {e}"