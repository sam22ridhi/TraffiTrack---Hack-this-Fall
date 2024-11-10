import setuptools

setuptools.setup(
    name="Traffictrack",
    version="0.1.5",
    author="Asmi",  # Replace with your name or organization
    author_email="asminparikh@gmail.com",  # Replace with your email
    description="An application integrating Auth0 for Traffictrack platform.",
    long_description="Traffictrack is a platform that integrates Auth0 to manage user authentication securely.",
    long_description_content_type="text/plain",
    url="https://github.com/yourusername/Traffictrack",  # Replace with the repository URL if available
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "streamlit >= 0.63",
        "python-jose == 3.3.0",
        "python-dotenv >= 0.15.0"
    ],
)
