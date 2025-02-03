from setuptools import setup, find_packages

setup(
    name="wordpress_api_client",
    version="0.1.0",
    description="A Python client for interacting with the WordPress REST API.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="nnevdokimov",
    author_email="nick.evdokimovv@gmail.com",
    url="https://github.com/nnevdokimov/wordpress_api_client",
    packages=find_packages(),
    install_requires=[
        "requests",
        "trackrace",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
