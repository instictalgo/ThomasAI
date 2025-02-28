from setuptools import setup, find_packages

setup(
    name="thomas_ai",
    version="1.07",
    description="AI-powered management system for game development projects",
    author="Thomas AI Team",
    author_email="your-email@example.com",
    url="https://github.com/yourusername/thomas_ai",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "fastapi<0.69.0",
        "uvicorn<0.16.0",
        "sqlalchemy<1.5.0",
        "pydantic<2.0.0",
        "requests",
        "python-dotenv==0.19.0",
        "streamlit<1.30.0",
        "plotly==5.6.0",
        "pandas<2.0.0",
        "protobuf==3.20.3",
        "python-multipart==0.0.5",
        "networkx>=2.5.1",
        "psutil",
        "pytest",
        # Document processing dependencies
        "PyPDF2==3.0.1",
        "python-docx==0.8.11",
        "openai==1.3.0",
        # PostgreSQL support
        "psycopg2-binary==2.9.3",
        # Enhanced knowledge management dependencies
        "scipy>=1.7.0",
        "numpy>=1.20.0"
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.12.0",
            "black>=21.5b2",
            "isort>=5.9.0",
            "flake8>=3.9.0",
            "mypy>=0.812",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.12",
    entry_points={
        "console_scripts": [
            "thomas-api=api.main:main",
            "thomas-dashboard=ui.dashboard:main",
        ],
    },
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
) 