import pytest
import sys

if __name__ == "__main__":
    print("Python executable:", sys.executable)
    print("Python version:", sys.version)
    print("Running pytest...")
    sys.exit(pytest.main(["test_basic.py", "-v"]))
