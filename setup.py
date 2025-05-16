from setuptools import setup, find_packages

setup(
    name="ferro-framework",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "flask>=2.0.0",
        "sqlalchemy>=1.4.0",
        "flask-cors>=3.0.0",
        "flask-socketio>=5.0.0",
    ],
    entry_points={
        'console_scripts': [
            'ferro=packages.cli.ferro:main',
        ],
    },
)
