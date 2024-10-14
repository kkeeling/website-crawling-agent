import asyncio
import os
from urllib.parse import urljoin, urlparse
from crawl4ai import AsyncWebCrawler
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from bs4 import BeautifulSoup
import json
import markdown
import signal

class WebsiteCrawlingAgent:
    def __init__(self, start_url, output_format='markdown', max_pages=None, output_folder=None):
        self.start_url = start_url
        self.output_format = output_format
        self.visited_urls = set()
        self.base_domain = urlparse(start_url).netloc
        self.output_folder = output_folder or f"output_{self.base_domain}"
        os.makedirs(self.output_folder, exist_ok=True)
        self.max_pages = max_pages
        self.pages_crawled = 0
        self.shutdown_flag = False

    async def crawl(self):
        print(f"Starting crawl from {self.start_url}")
        async with AsyncWebCrawler(verbose=True) as crawler:
            await self.crawl_page(crawler, self.start_url)
        print(f"\nCrawl completed. Output saved in {self.output_folder}")
        print(f"Total pages crawled: {self.pages_crawled}")

    async def crawl_page(self, crawler, url):
        if self.shutdown_flag or (self.max_pages and self.pages_crawled >= self.max_pages):
            return

        # Remove anchor from URL
        url = url.split('#')[0]

        if url in self.visited_urls or not url.startswith(('http://', 'https://')):
            return

        self.visited_urls.add(url)
        self.pages_crawled += 1
        print(f"\rCrawling page {self.pages_crawled}: {url}", end='', flush=True)

        extraction_strategy = LLMExtractionStrategy(
            instruction="Extract the main content, including headings, paragraphs, and any important information. Ignore navigation menus, footers, and sidebars."
        )

        try:
            result = await crawler.arun(url=url, extraction_strategy=extraction_strategy)

            if result.success and result.status_code != 404:
                content = result.extracted_content
                
                # Check if the page is a custom 404 page
                soup = BeautifulSoup(result.html, 'html.parser')
                if "404" in soup.title.string.lower() or "not found" in soup.title.string.lower():
                    print(f"\nSkipping 404 page: {url}")
                    return

                self.save_content(url, content)

                links = soup.find_all('a', href=True)
                for link in links:
                    next_url = urljoin(url, link['href'])
                    next_url = next_url.split('#')[0]  # Remove anchor
                    if urlparse(next_url).netloc == self.base_domain:
                        await self.crawl_page(crawler, next_url)
            elif result.status_code == 404:
                print(f"\nSkipping 404 page: {url}")
            else:
                print(f"\nFailed to crawl {url}: {result.error_message}")
        except Exception as e:
            print(f"\nError crawling {url}: {str(e)}")

    def save_content(self, url, content):
        relative_path = urlparse(url).path.strip('/') or 'index'
        filename = os.path.join(self.output_folder, f"{relative_path}.{self.output_format}")
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        if self.output_format == 'markdown':
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"# {url}\n\n{content}")
        elif self.output_format == 'json':
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump({"url": url, "content": content}, f, ensure_ascii=False, indent=2)
        elif self.output_format == 'pdf':
            # For PDF, we'll first convert to HTML, then use a library like pdfkit to convert to PDF
            html_content = markdown.markdown(f"# {url}\n\n{content}")
            pdfkit.from_string(html_content, filename)
        else:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)

        print(f"\nSaved content from {url} to {filename}")

    def shutdown(self):
        print("\nShutting down gracefully. Please wait for the current page to finish...")
        self.shutdown_flag = True

async def main():
    start_url = input("Enter the starting URL: ")
    output_format = input("Enter the output format (markdown/json/pdf/txt, default: markdown): ").lower() or 'markdown'
    max_pages = input("Enter the maximum number of pages to crawl (leave blank for no limit): ")
    max_pages = int(max_pages) if max_pages.isdigit() else None
    output_folder = input("Enter the output folder name (leave blank for default): ")
    output_location = input("Enter the output folder location (leave blank for current directory): ")
    
    if output_folder and output_location:
        output_folder = os.path.join(output_location, output_folder)
    elif output_folder:
        output_folder = os.path.join(os.getcwd(), output_folder)
    elif output_location:
        output_folder = os.path.join(output_location, f"output_{urlparse(start_url).netloc}")
    else:
        output_folder = None  # Will use the default in the WebsiteCrawlingAgent constructor
    
    agent = WebsiteCrawlingAgent(start_url, output_format, max_pages, output_folder)
    
    def signal_handler(signum, frame):
        agent.shutdown()
    
    signal.signal(signal.SIGINT, signal_handler)
    
    await agent.crawl()

if __name__ == "__main__":
    asyncio.run(main())
