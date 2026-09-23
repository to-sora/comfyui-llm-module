import subprocess
from .acceptance import main as acceptance
from .report import checked
from .setup import APP, configure


def main():
    def check():
        configure()
        return acceptance()
    try:
        checked(check)
    finally:
        subprocess.run([str(APP / "start.sh"), "--stop"], check=True)


if __name__ == "__main__":
    main()
