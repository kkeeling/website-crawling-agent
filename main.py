import asyncio
import os
from urllib.parse import urljoin, urlparse
from crawl4ai import AsyncWebCrawler
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from bs4 import BeautifulSoup
import json
import markdown

class WebsiteCrawlingAgent:
    def __init__(self, start_url, output_format='markdown'):
        self.start_url = start_url
        self.output_format = output_format
        self.visited_urls = set()
        self.base_domain = urlparse(start_url).netloc
        self.output_folder = f"output_{self.base_domain}"
        os.makedirs(self.output_folder, exist_ok=True)

    async def crawl(self):
        print(f"Starting crawl from {self.start_url}")
        async with AsyncWebCrawler(verbose=True) as crawler:
            await self.crawl_page(crawler, self.start_url)
        print(f"Crawl completed. Output saved in {self.output_folder}")

    async def crawl_page(self, crawler, url):
        if url in self.visited_urls or not url.startswith(('http://', 'https://')):
            return

        self.visited_urls.add(url)
        print(f"Crawling: {url}")

        extraction_strategy = LLMExtractionStrategy(
            instruction="Extract the main content, including headings, paragraphs, and any important information. Ignore navigation menus, footers, and sidebars."
        )

        result = await crawler.arun(url=url, extraction_strategy=extraction_strategy)

        if result.success:
            content = result.extracted_content
            self.save_content(url, content)

            soup = BeautifulSoup(result.html, 'html.parser')
            links = soup.find_all('a', href=True)
            for link in links:
                next_url = urljoin(url, link['href'])
                if urlparse(next_url).netloc == self.base_domain:
                    await self.crawl_page(crawler, next_url)
        else:
            print(f"Failed to crawl {url}: {result.error_message}")

    def save_content(self, url, content):
        filename = os.path.join(self.output_folder, f"{urlparse(url).path.strip('/') or 'index'}.{self.output_format}")
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        if self.output_format == 'markdown':
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"# {url}\n\n{content}")
        elif self.output_format == 'pdf':
            # For PDF, we'll first convert to HTML, then use a library like pdfkit to convert to PDF
            html_content = markdown.markdown(f"# {url}\n\n{content}")
            pdfkit.from_string(html_content, filename)
        else:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)

        print(f"Saved content from {url} to {filename}")

async def main():
    start_url = input("Enter the starting URL: ")
    output_format = input("Enter the output format (markdown/pdf/txt, default: markdown): ").lower() or 'markdown'
    
    agent = WebsiteCrawlingAgent(start_url, output_format)
    await agent.crawl()

if __name__ == "__main__":
    asyncio.run(main())
