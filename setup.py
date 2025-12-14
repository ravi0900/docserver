from setuptools import setup, find_packages

setup(
    name="docserver",
    version="0.1.0",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    package_data={"docserver": ["templates/*.html"]},
    install_requires=[
        "Flask",
        "mistune",
    ],
    entry_points={
        "console_scripts": [
            "docserver = docserver.__main__:main",
        ],
    },
)
