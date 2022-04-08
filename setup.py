import setuptools

with open("README_en.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pydicom_tools",
    version="0.0.10",
    author="Akihisa Wakita",
    author_email="wakita84@gmail.com",
    description="Tools for dicom RT analysis with pydicom",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/wkt84/pydicom-tools",
    packages=setuptools.find_packages(),
    install_requires=[
        "pydicom",
        "numpy",
        "matplotlib",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
