import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="imdb_cli_tool",
    version="0.0.4",
    author="Zak Cook",
    author_email="1zrcook@gmail.com",
    description="A cli tool to pull movie information about actors/actresses.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Zocozoro/imdb",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
