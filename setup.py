import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="django_param_validator",
    version="0.0.1",
    author="Paul Wayper",
    author_email="paulway@mabula.net",
    description="Use OpenAPI Parameter objects to validate Django query parameters",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/PaulWay/django-param-validator",
    packages=setuptools.find_packages(),
    classifiers=[
        "Framework :: Django :: 2.1",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content :: Content Management System",
    ],
)
