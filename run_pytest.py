import subprocess
import sys

def run_pytest():
    try:
        # Exécute pytest avec subprocess pour un meilleur contrôle
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "test_math.py", "-v"],
            capture_output=True,
            text=True
        )
        
        # Affiche la sortie
        print("=== STDOUT ===")
        print(result.stdout)
        print("\n=== STDERR ===")
        print(result.stderr)
        
    except Exception as e:
        print(f"Erreur lors de l'exécution de pytest: {e}")

if __name__ == "__main__":
    run_pytest()
