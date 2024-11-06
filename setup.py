from setuptools import setup, find_packages
from setuptools.command.develop import develop
from setuptools.command.install import install
import subprocess

class PostDevelopCommand(develop):
    """Post-installation for development mode."""
    def run(self):
        develop.run(self)
        try:
            # Use python -m playwright for more reliable execution
            subprocess.check_call(['python', '-m', 'playwright', 'install', 'chromium'])
        except subprocess.CalledProcessError as e:
            print("Warning: Failed to install Playwright browser automatically.")
            print("Please run 'python -m playwright install chromium' manually after installation.")
            print(f"Error was: {e}")

class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        install.run(self)
        try:
            # Use python -m playwright for more reliable execution
            subprocess.check_call(['python', '-m', 'playwright', 'install', 'chromium'])
        except subprocess.CalledProcessError as e:
            print("Warning: Failed to install Playwright browser automatically.")
            print("Please run 'python -m playwright install chromium' manually after installation.")
            print(f"Error was: {e}")

setup(
    cmdclass={
        'develop': PostDevelopCommand,
        'install': PostInstallCommand,
    },
    name="website-crawling-agent",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "crawl4ai>=0.3.73",
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
