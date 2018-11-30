import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name = 'pyTeamUp',
    version = '0.1.0a1',
    author = 'David Jones',
    author_email = 'David.jone4822@gmail.com',
    description = 'Python wrapper for TeamUp Calendar\'s API',
    long_description = long_description,
    long_description_content_tpye = "text/markdown",
    url = "https://github.com/DJones4822/pyTeamUp",
    packages = setuptools.find_packages(),
    classifiers = ["Programming Language :: Python :: 3",
                   "License :: OSI Approved :: MIT License",
                   "Operating System :: OS Independent"],
)