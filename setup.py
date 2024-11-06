from setuptools import setup, find_packages
from setuptools.command.develop import develop
from setuptools.command.install import install
import subprocess
import sys
import time

def install_playwright_browser(retries=3, delay=2):
    """Install Playwright browser with retries."""
    for attempt in range(retries):
        try:
            # Ensure playwright is installed first
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'playwright'])
            
            # Then install the browser
            subprocess.check_call([sys.executable, '-m', 'playwright', 'install', 'chromium'])
            print("Successfully installed Playwright browser (Chromium)")
            return True
        except subprocess.CalledProcessError as e:
            if attempt < retries - 1:
                print(f"Attempt {attempt + 1} failed. Retrying in {delay} seconds...")
                time.sleep(delay)
                delay *= 2  # Exponential backoff
            else:
                print("\nWarning: Failed to install Playwright browser automatically.")
                print("Error details:")
                print(f"Command '{' '.join(e.cmd)}' failed with exit status {e.returncode}")
                print(f"Error output: {e.output if hasattr(e, 'output') else 'No output available'}")
                print("\nPlease try installing manually after installation completes:")
                print("1. pip install playwright")
                print("2. python -m playwright install chromium")
                return False
        except Exception as e:
            print(f"\nUnexpected error while installing Playwright browser: {str(e)}")
            print("Please install manually using the steps above.")
            return False

class PostDevelopCommand(develop):
    """Post-installation for development mode."""
    def run(self):
        develop.run(self)
        install_playwright_browser()

class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        install.run(self)
        install_playwright_browser()

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
