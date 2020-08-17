from setuptools import setup, find_packages

# Read the README.md file
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="up2ynab",
    version="0.0.1.dev0",
    description="CLI for synchronising the Up neobank with YNAB",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lachholden/up2ynab",
    author="Lachlan H",
    author_email="lachlan.holden@gmail.com",
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.8",
        "Topic :: Office/Business :: Financial",
        "Topic :: Utilities",
    ],
    keywords="cli bank import sync YNAB Up",
    python_requires=">=3",
    packages=find_packages(),
    include_package_data=True,
    install_requires=["click", "requests"],
    entry_points="""
        [console_scripts]
        up2ynab=up2ynab:cli
    """,
)
