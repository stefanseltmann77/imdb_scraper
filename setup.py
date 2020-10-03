import setuptools

with open("README.rst", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="imdb_assetscraper",
    version="0.1.2",
    author="Stefan Seltmann",
    author_email="s.seltmann06@web.de",
    description="imdb_assetscraper",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url='https://github.com/stefanseltmann77/imdb_scraper',
    packages=['imdb_assetscraper'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
