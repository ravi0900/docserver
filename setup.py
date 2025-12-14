from setuptools import setup, find_packages

setup(
    name="docserver",
    version="0.1.0",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    include_package_data=True,
    install_requires=[
        "watchdog",
        "Flask",
        "GitPython",
        "mistune",
    ],
    entry_points={
        "console_scripts": [
            "docserver = docserver.__main__:main",
        ],
    },
)