import os
from urllib.parse import urljoin, urlparse
from crawl4ai import AsyncWebCrawler
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from bs4 import BeautifulSoup
import json
import markdown
import pdfkit

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

        # Check domain boundary
        if urlparse(url).netloc != self.base_domain:
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
                title = soup.title.string if soup.title else ""
                if title and ("404" in title.lower() or "not found" in title.lower()):
                    print(f"\nSkipping 404 page: {url}")
                    return

                self.save_content(url, content)

                # Only process links if we haven't hit max pages
                if not self.max_pages or self.pages_crawled < self.max_pages:
                    links = soup.find_all('a', href=True)
                    for link in links:
                        next_url = urljoin(url, link['href'])
                        next_url = next_url.split('#')[0]  # Remove anchor
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
            html_content = f"<h1>{url}</h1>\n<p>{content}</p>"
            pdfkit.from_string(html_content, filename)
        else:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)

    def shutdown(self):
        print("\nShutting down gracefully. Please wait for the current page to finish...")
        self.shutdown_flag = True
