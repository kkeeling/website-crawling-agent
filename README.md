# Website Crawling Agent

This agent uses the crawl4ai library to crawl websites, extract important information from each page, and save the content in a specified format.

## Features

- Crawls all pages within a given domain
- Extracts important information using LLM-based extraction
- Supports multiple output formats (markdown, JSON, PDF, plain text)
- Provides real-time feedback on crawling progress
- Allows setting a maximum number of pages to crawl
- Implements graceful shutdown on keyboard interrupt
- Skips processing and storing 404 pages (both HTTP 404 and custom 404 pages)
- Ignores URL anchors, treating URLs with different anchors as the same page
- Allows user to specify the name and location of the output folder

## Installation

You can install the package using pip:

```bash
pip install website-crawling-agent
```

Or for a isolated installation using pipx:

```bash
pipx install website-crawling-agent
```

### Additional Setup

1. If you want to use PDF output, install wkhtmltopdf:
   - On macOS: `brew install wkhtmltopdf`
   - On Ubuntu: `sudo apt-get install wkhtmltopdf`
   - On Windows: Download and install from https://wkhtmltopdf.org/downloads.html

3. Set up your OpenAI API key:
   ```
   export OPENAI_API_KEY=your_api_key_here
   ```

## Usage

Run the command:

```bash
web-crawl URL [options]
```

For example:
```bash
web-crawl https://example.com --format markdown --max-pages 10 --output-folder ./output
```

Available options:
- `--format` or `-f`: Output format (markdown, json, pdf, or txt)
- `--max-pages` or `-m`: Maximum number of pages to crawl
- `--output-folder` or `-o`: Output folder path

The crawler will process:
1. The starting URL for the crawl
2. The desired output format (markdown, json, pdf, or txt)
3. The maximum number of pages to crawl (optional)
4. The name of the output folder (optional)
5. The location of the output folder (optional)

The agent will then crawl the website, providing feedback on its progress. The extracted content will be saved in the specified output folder or in an `output_[domain]` folder in the current directory if not specified.

## Customization

- Modify the `LLMExtractionStrategy` instruction in the `crawl_page` method to customize the content extraction.
- Adjust the `save_content` method to support additional output formats if needed.

## Notes

- The agent respects the domain boundaries and only crawls pages within the same domain as the starting URL.
- Be mindful of the website's robots.txt file and terms of service when using this crawler.
- You can stop the crawling process at any time by pressing Ctrl+C. The agent will finish processing the current page before shutting down.
- The agent skips processing and storing 404 pages, including custom 404 pages detected by their title.
- URLs with different anchors (e.g., `http://example.com/page#section1` and `http://example.com/page#section2`) are treated as the same page to avoid duplicate crawling.
- You can specify the name and location of the output folder. If not specified, the default is `output_[domain]` in the current directory.
