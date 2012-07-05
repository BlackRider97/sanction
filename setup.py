import os
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, "README.rst")).read()

requires = []

setup(name="sanction",
	keywords="python,oauth2",
    version="0.1-alpha-3",
    description="A simple, lightweight OAuth2 client",
    author="Demian Brecht",
    author_email="demianbrecht@gmail.com",
	url="https://github.com/demianbrecht/sanction",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Site Management",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Systems Administration :: Authentication/Directory"
    ],
    long_description=README,
    install_requires=requires,
	packages=["sanction",]
)
