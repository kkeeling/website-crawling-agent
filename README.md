# Website Crawling Agent

This agent uses the crawl4ai library to crawl websites, extract important information from each page, and save the content in a specified format.

## Features

- Crawls all pages within a given domain
- Extracts important information using LLM-based extraction
- Supports multiple output formats (markdown, PDF, plain text)
- Provides real-time feedback on crawling progress
- Allows setting a maximum number of pages to crawl
- Implements graceful shutdown on keyboard interrupt

## Setup

1. Install the required dependencies:

```
pip install -r requirements.txt
```

2. If you want to use PDF output, install wkhtmltopdf:
   - On macOS: `brew install wkhtmltopdf`
   - On Ubuntu: `sudo apt-get install wkhtmltopdf`
   - On Windows: Download and install from https://wkhtmltopdf.org/downloads.html

3. Set up your OpenAI API key:
   ```
   export OPENAI_API_KEY=your_api_key_here
   ```

## Usage

Run the script:

```
python main.py
```

You will be prompted to enter:
1. The starting URL for the crawl
2. The desired output format (markdown, pdf, or txt)
3. The maximum number of pages to crawl (optional)

The agent will then crawl the website, providing feedback on its progress. The extracted content will be saved in an `output_[domain]` folder.

## Customization

- Modify the `LLMExtractionStrategy` instruction in the `crawl_page` method to customize the content extraction.
- Adjust the `save_content` method to support additional output formats if needed.

## Notes

- The agent respects the domain boundaries and only crawls pages within the same domain as the starting URL.
- Be mindful of the website's robots.txt file and terms of service when using this crawler.
- You can stop the crawling process at any time by pressing Ctrl+C. The agent will finish processing the current page before shutting down.
