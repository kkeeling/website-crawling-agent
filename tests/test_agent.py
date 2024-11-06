import pytest
import os
import json
import asyncio
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
