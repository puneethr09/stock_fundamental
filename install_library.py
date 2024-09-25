import subprocess
import sys


def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])


# List of required packages
packages = [
    "pandas",
    "yfinance",
    "matplotlib",
    "nltk",
    "scikit-learn",
    "tabulate",
    "seaborn",
]

# Install each package
for package in packages:
    install(package)
