import asyncio
import argparse
from .agent import WebsiteCrawlingAgent

def parse_args():
    parser = argparse.ArgumentParser(description="Crawl websites and extract information using LLMs")
    parser.add_argument("url", help="Starting URL to crawl")
    parser.add_argument("--format", "-f", 
                      choices=["markdown", "json", "pdf", "txt"],
                      default="markdown",
                      help="Output format (default: markdown)")
    parser.add_argument("--max-pages", "-m", 
                      type=int,
                      help="Maximum number of pages to crawl")
    parser.add_argument("--output-folder", "-o",
                      help="Output folder path")
    return parser.parse_args()

def main():
    args = parse_args()
    agent = WebsiteCrawlingAgent(
        start_url=args.url,
        output_format=args.format,
        max_pages=args.max_pages,
        output_folder=args.output_folder
    )
    
    try:
        asyncio.run(agent.crawl())
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
        agent.shutdown()

if __name__ == "__main__":
    main()
