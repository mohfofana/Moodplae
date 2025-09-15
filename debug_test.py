import sys
import os
import importlib

def main():
    print("=== Debug Information ===")
    print(f"Python executable: {sys.executable}")
    print(f"Python version: {sys.version}")
    print(f"Current directory: {os.getcwd()}")
    
    # Vérifier l'installation de pytest
    try:
        import pytest
        print(f"pytest version: {pytest.__version__}")
        
        # Exécuter un test simple
        print("\nRunning simple test...")
        test_code = """
def test_simple():
    print("Test is running!")
    assert 1 + 1 == 2
"""
        with open("_temp_test.py", "w") as f:
            f.write(test_code)
            
        result = pytest.main(["_temp_test.py", "-v"])
        print(f"Test result: {result}")
        
        # Nettoyer
        if os.path.exists("_temp_test.py"):
            os.remove("_temp_test.py")
            
    except ImportError as e:
        print(f"Error importing pytest: {e}")
        print("Please install pytest using: pip install pytest")

if __name__ == "__main__":
    main()
