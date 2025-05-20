from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="UnitCostKitchen",
    version="0.1.0",
    author="Claudio Ariza",
    author_email="clarba156@gmail.com",
    description="UnitCostKitchen: Modular software for kitchen designers/sellers.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/claudioAB-dev/UnitCostKitchen",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "requests>=2.25.1",
        "numpy>=1.20.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
