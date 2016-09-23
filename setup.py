from setuptools import setup, find_packages

VERSION = '1.0.10'

setup(
    name="reporters-db",
    description="Database of Court Reporters",
    version=VERSION,
    author="Mike Lissner",
    author_email="info@free.law",
    maintainer="Mike Lisser",
    maintainer_email="info@free.law",
    packages=find_packages(exclude=('tests',)),
    include_package_data=True,
    package_data={
        'reporters_db': [
            'data/*',
        ]
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    test_suite="tests",
)
