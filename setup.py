import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mathjson-solver",
    version="1.0.1",
    author="Martins Mednis",
    author_email="mrt@mednis.info",
    description="Utilities for MathJSON evaluation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/LongenesisLtd/mathjson-solver",
    project_urls={
        "Bug Tracker": "https://github.com/LongenesisLtd/mathjson-solver/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)
