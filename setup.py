from setuptools import setup, find_packages

setup(
    name="up2ynab",
    version="0.0.1-dev",
    packages=find_packages(),
    include_package_data=True,
    install_requires=["Click",],
    entry_points="""
        [console_scripts]
        up2ynab=up2ynab:cli
    """,
)
