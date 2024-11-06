from setuptools import setup, find_packages

setup(
    name="website-crawling-agent",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "crawl4ai~=1.0.0",
        "beautifulsoup4>=4.12.0",
        "markdown>=3.5.0",
        "pdfkit>=1.0.0",
        "litellm==1.51.2",
        "requests==2.32.3",
        "urllib3~=2.0.0",
        "playwright>=1.40.0",
    ],
    extras_require={
        'test': [
            'pytest>=7.4.0',
            'pytest-asyncio>=0.21.0'
        ]
    },
    entry_points={
        'console_scripts': [
            'web-crawl=website_crawling_agent.cli:main',
        ],
    },
    author="Your Name",
    description="A website crawling agent that extracts information using LLMs",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/website-crawling-agent",
    python_requires=">=3.7",
)
