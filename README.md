# Website Crawling Agent

This agent uses the crawl4ai library to crawl websites, extract important information from each page, and save the content in a specified format.

## Features

- Crawls all pages within a given domain
- Extracts important information using LLM-based extraction
- Supports multiple output formats (markdown, PDF, plain text)
- Provides real-time feedback on crawling progress

## Setup

1. Install Miniconda or Anaconda if you haven't already:
   - Download from: https://docs.conda.io/en/latest/miniconda.html

2. Create a new conda environment:
   ```
   conda create -n website-crawler python=3.9
   ```

3. Activate the conda environment:
   ```
   conda activate website-crawler
   ```

4. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

5. If you want to use PDF output, install wkhtmltopdf:
   - On macOS: `brew install wkhtmltopdf`
   - On Ubuntu: `sudo apt-get install wkhtmltopdf`
   - On Windows: Download and install from https://wkhtmltopdf.org/downloads.html

6. Set up your OpenAI API key:
   ```
   export OPENAI_API_KEY=your_api_key_here
   ```

## Usage

Ensure you're in the conda environment:
```
conda activate website-crawler
```

Then run the script:
```
python main.py
```

You will be prompted to enter:
1. The starting URL for the crawl
2. The desired output format (markdown, pdf, or txt)

The agent will then crawl the website, providing feedback on its progress. The extracted content will be saved in an `output_[domain]` folder.

## Customization

- Modify the `LLMExtractionStrategy` instruction in the `crawl_page` method to customize the content extraction.
- Adjust the `save_content` method to support additional output formats if needed.

## Notes

- The agent respects the domain boundaries and only crawls pages within the same domain as the starting URL.
- Be mindful of the website's robots.txt file and terms of service when using this crawler.

## Deactivating the Environment

When you're done using the agent, you can deactivate the conda environment:
```
conda deactivate
