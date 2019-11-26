import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name="mozfederatedpolicybuilder",
    version="0.1.0",
    author="Gene Wood",
    author_email='gene_wood@cementhorizon.com',
    description="Tool to create an AWS IAM Role with a federated policy "
                "allowing users to login with Single Sign On",
    extras_require={
        "test": [
            "pytest",
            "pytest-cov",
            "pytest-clarity",
            'mock;python_version<"3.3"']
    },
    entry_points={
        'console_scripts': [
            'mozfederatedpolicybuilder=mozfederatedpolicybuilder:main',
        ],
    },
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=["PyYAML"],
    url="https://github.com/mozilla-iam/mozfederatedpolicybuilder",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Code Generators",
    ],
)
