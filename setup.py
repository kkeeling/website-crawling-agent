from setuptools import setup, find_packages

setup(
    name="website-crawling-agent",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "crawl4ai",
        "beautifulsoup4",
        "markdown",
        "pdfkit",
    ],
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
