from setuptools import setup, find_packages
from tmanager import tman_name, tman_version, tman_description, tman_url

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name=tman_name,
    version=tman_version,
    url=tman_url,
    license="MIT",
    description=tman_description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="ssh3ll",
    author_email="ssh3ll at protonmail.com",
    maintainer="Valerio Preti",
    maintainer_email="valerio.preti.tman at gmail.com",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "click>=7.0",
        "GitPython>=2.1.11",
        "python-crontab>=2.3.6",
    ],
    setup_requires=[
        "pytest-runner>=4.4",
    ],
    tests_require=[
        "pytest>=4.4",
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "tman = tmanager.tman:tman",
        ],
    },
    classifiers=[
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.7",
    ],
)
