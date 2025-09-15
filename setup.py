from setuptools import setup, find_packages

setup(
    name="moodplay_phi",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        'numpy>=1.21.0',
        'scipy>=1.7.0',
        'scikit-learn>=1.0.0',
        'pydantic>=1.8.0',
        'python-dateutil>=2.8.2',
        'pytz>=2021.1',
    ],
    python_requires='>=3.8',
)
