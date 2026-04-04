from setuptools import setup, find_packages

setup(
    name="playbook-pulse-agents",
    version="1.0.0",
    description="Multi-agent backend for PlaybookPulse incident response compliance analysis",
    author="Your Team",
    author_email="team@yourdomain.com",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "fastapi>=0.109.0",
        "uvicorn[standard]>=0.27.0",
        "pydantic>=2.5.3",
        "anthropic>=0.18.1",
        "httpx>=0.26.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.4",
            "pytest-asyncio>=0.23.3",
            "pytest-cov>=4.1.0",
            "black>=24.1.1",
            "isort>=5.13.2",
            "flake8>=7.0.0",
        ],
        "integrations": [
            "slack-sdk>=3.26.2",
            "jira>=3.6.0",
            "PyGithub>=2.1.1",
        ],
    },
    entry_points={
        "console_scripts": [
            "playbook-pulse=app.main:main",
        ],
    },
)
