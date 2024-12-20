import pytest
import os
import json
import asyncio
import sys
import subprocess
from unittest.mock import Mock, patch, AsyncMock
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from website_crawling_agent.agent import WebsiteCrawlingAgent

@pytest.fixture
def agent():
    return WebsiteCrawlingAgent("https://example.com")

@pytest.fixture
def mock_crawler():
    crawler = AsyncMock()
    return crawler

class MockCrawlResult:
    def __init__(self, success=True, status_code=200, content="Test content", html="<html><title>Test</title></html>"):
        self.success = success
        self.status_code = status_code
        self.extracted_content = content
        self.html = html
        self.error_message = None if success else "Error"

def test_init():
    """Test the initialization of WebsiteCrawlingAgent"""
    agent = WebsiteCrawlingAgent(
        start_url="https://example.com",
        output_format="json",
        max_pages=10,
        output_folder="custom_output"
    )
    
    assert agent.start_url == "https://example.com"
    assert agent.output_format == "json"
    assert agent.max_pages == 10
    assert agent.output_folder == "custom_output"
    assert agent.base_domain == "example.com"
    assert agent.pages_crawled == 0
    assert agent.shutdown_flag is False
    assert isinstance(agent.visited_urls, set)

@pytest.mark.asyncio
async def test_crawl(agent, mock_crawler):
    """Test the crawl method"""
    with patch('website_crawling_agent.agent.AsyncWebCrawler') as MockCrawler:
        MockCrawler.return_value.__aenter__.return_value = mock_crawler
        await agent.crawl()
        mock_crawler.arun.assert_called()

@pytest.mark.asyncio
async def test_crawl_page_normal(agent, mock_crawler):
    """Test crawling a normal page"""
    mock_result = MockCrawlResult()
    mock_crawler.arun.return_value = mock_result
    
    url = "https://example.com/page1"
    await agent.crawl_page(mock_crawler, url)
    
    assert url in agent.visited_urls
    assert agent.pages_crawled == 1
    mock_crawler.arun.assert_called_once()

@pytest.mark.asyncio
async def test_crawl_page_404(agent, mock_crawler):
    """Test crawling a 404 page"""
    mock_result = MockCrawlResult(status_code=404)
    mock_crawler.arun.return_value = mock_result
    
    url = "https://example.com/nonexistent"
    await agent.crawl_page(mock_crawler, url)
    
    assert url in agent.visited_urls
    assert agent.pages_crawled == 1

@pytest.mark.asyncio
async def test_crawl_page_custom_404(agent, mock_crawler):
    """Test crawling a custom 404 page"""
    mock_result = MockCrawlResult(html="<html><title>404 Not Found</title></html>")
    mock_crawler.arun.return_value = mock_result
    
    url = "https://example.com/custom404"
    await agent.crawl_page(mock_crawler, url)
    
    assert url in agent.visited_urls
    assert agent.pages_crawled == 1

@pytest.mark.asyncio
async def test_max_pages_limit(agent, mock_crawler):
    """Test respecting max_pages limit"""
    agent.max_pages = 1
    mock_result = MockCrawlResult()
    mock_crawler.arun.return_value = mock_result
    
    await agent.crawl_page(mock_crawler, "https://example.com/page1")
    await agent.crawl_page(mock_crawler, "https://example.com/page2")
    
    assert agent.pages_crawled == 1
    assert len(agent.visited_urls) == 1

def test_save_content(agent, tmp_path):
    """Test saving content in different formats"""
    agent.output_folder = str(tmp_path)
    url = "https://example.com/test"
    content = "Test content"

    # Test markdown format
    agent.output_format = "markdown"
    agent.save_content(url, content)
    markdown_file = tmp_path / "test.markdown"
    assert markdown_file.exists()
    assert "# https://example.com/test" in markdown_file.read_text()

    # Test JSON format
    agent.output_format = "json"
    agent.save_content(url, content)
    json_file = tmp_path / "test.json"
    assert json_file.exists()
    saved_json = json.loads(json_file.read_text())
    assert saved_json["url"] == url
    assert saved_json["content"] == content

    # Test txt format
    agent.output_format = "txt"
    agent.save_content(url, content)
    txt_file = tmp_path / "test.txt"
    assert txt_file.exists()
    assert content in txt_file.read_text()

def test_shutdown(agent):
    """Test shutdown method"""
    agent.shutdown()
    assert agent.shutdown_flag is True

@pytest.mark.asyncio
async def test_url_anchor_handling(agent, mock_crawler):
    """Test that URLs with different anchors are treated as the same page"""
    mock_result = MockCrawlResult()
    mock_crawler.arun.return_value = mock_result
    
    # Crawl URL with anchor
    url1 = "https://example.com/page#section1"
    await agent.crawl_page(mock_crawler, url1)
    
    # Attempt to crawl same URL with different anchor
    url2 = "https://example.com/page#section2"
    await agent.crawl_page(mock_crawler, url2)
    
    # Should only count as one page
    assert agent.pages_crawled == 1
    assert len(agent.visited_urls) == 1
    assert "https://example.com/page" in agent.visited_urls

@pytest.mark.asyncio
async def test_domain_boundary(agent, mock_crawler):
    """Test that the crawler respects domain boundaries"""
    mock_result = MockCrawlResult(
        html="""
        <html>
            <body>
                <a href="https://example.com/internal">Internal Link</a>
                <a href="https://otherdomain.com/external">External Link</a>
            </body>
        </html>
        """
    )
    mock_crawler.arun.return_value = mock_result
    
    url = "https://example.com/start"
    await agent.crawl_page(mock_crawler, url, test_mode=True)
    
    # Should only have visited the start URL
    assert len(agent.visited_urls) == 1
    assert "https://example.com/start" in agent.visited_urls
    assert "https://otherdomain.com/external" not in agent.visited_urls

@pytest.mark.asyncio
async def test_error_handling(agent, mock_crawler):
    """Test handling of crawling errors"""
    mock_result = MockCrawlResult(success=False)
    mock_crawler.arun.return_value = mock_result
    
    url = "https://example.com/error-page"
    await agent.crawl_page(mock_crawler, url)
    
    # Should still mark URL as visited despite error
    assert url in agent.visited_urls
    assert agent.pages_crawled == 1

@pytest.mark.asyncio
async def test_pdf_output(agent, tmp_path):
    """Test PDF output format with mocked pdfkit"""
    with patch('website_crawling_agent.agent.pdfkit') as mock_pdfkit:
        agent.output_folder = str(tmp_path)
        agent.output_format = "pdf"
        
        url = "https://example.com/test"
        content = "Test content"
        
        agent.save_content(url, content)
        
        expected_html = "<h1>https://example.com/test</h1>\n<p>Test content</p>"
        expected_output_path = os.path.join(str(tmp_path), "test.pdf")
        mock_pdfkit.from_string.assert_called_once_with(
            expected_html,
            expected_output_path
        )

@patch('website_crawling_agent.agent.subprocess.check_call')
@patch('website_crawling_agent.agent.Path.exists')
def test_check_playwright_browser_success(mock_path_exists, mock_check_call):
    """Test successful Playwright browser check and installation"""
    # Mock all possible paths to return False initially
    mock_path_exists.side_effect = [False] * 5  # For all 5 possible paths
    
    # Create agent which will trigger browser check
    agent = WebsiteCrawlingAgent("https://example.com")
    
    # Mock successful installation
    mock_check_call.return_value = 0
    
    # Verify installation was attempted
    mock_check_call.assert_called_once_with(
        [sys.executable, '-m', 'playwright', 'install', 'chromium'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

@patch('website_crawling_agent.agent.subprocess.check_call')
@patch('website_crawling_agent.agent.Path.exists')
def test_check_playwright_browser_failure(mock_path_exists, mock_check_call):
    """Test failed Playwright browser installation"""
    mock_path_exists.return_value = False
    mock_check_call.side_effect = subprocess.CalledProcessError(
        1, 'command', stderr=b'Error message'
    )
    
    with pytest.raises(SystemExit) as cm:
        agent = WebsiteCrawlingAgent("https://example.com")
    assert cm.value.code == 1

@patch('website_crawling_agent.agent.Path.exists')
def test_check_playwright_browser_unexpected_error(mock_path_exists):
    """Test unexpected error during browser check"""
    mock_path_exists.side_effect = Exception('Unexpected error')
    
    with pytest.raises(SystemExit) as cm:
        agent = WebsiteCrawlingAgent("https://example.com")
    assert cm.value.code == 1

@patch('website_crawling_agent.agent.Path.exists')
def test_check_playwright_browser_already_installed(mock_path_exists):
    """Test when Playwright browser is already installed"""
    # Simulate browser already being installed
    mock_path_exists.return_value = True
    
    agent = WebsiteCrawlingAgent("https://example.com")
    # Should not raise any exceptions
    agent.check_playwright_browser()
