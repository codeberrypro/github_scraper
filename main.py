import os
import json
import random
import logging
import asyncio

import aiohttp
from dotenv import load_dotenv
from bs4 import BeautifulSoup

load_dotenv()
logging.basicConfig(
    filename='data/logs.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


class GitHubCrawler:
    def __init__(self, keywords, proxies, search_type):
        self.keywords = keywords
        self.proxies = proxies
        self.proxies_login = os.getenv('PROXY_LOGIN')
        self.proxies_password = os.getenv('PROXY_PASSWORD')
        self.search_type = search_type
        self.base_urls = self.create_base_urls()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
                          ' AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }

    def create_base_urls(self):
        # Create a list of URLs for each keyword
        return [f"https://github.com/search?q={keyword}&type={self.search_type}" for keyword in self.keywords]

    async def make_request(self, session, url):
        proxy = random.choice(self.proxies)
        proxy_url = f"http://{self.proxies_login}:{self.proxies_password}@{proxy}"
        try:
            async with session.get(url, proxy=proxy_url, headers=self.headers, timeout=10) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    logging.error(f"Error: {response.status} for URL: {url}")
                    return None
        except Exception as e:
            logging.error(f"Request error: {e} for URL: {url}")
            return None

    async def extract_repo_data(self, session, url):
        html = await self.make_request(session, url)
        if not html:
            logging.warning(f"No HTML response for URL: {url}")
            return None

        soup = BeautifulSoup(html, 'html.parser')
        owner_tag = soup.find('a', {'rel': 'author'})
        owner = owner_tag.text.strip() if owner_tag else "Not found"

        languages = {}  # Extract language statistics
        for language_block in soup.find_all('li', {'class': 'd-inline'}):
            language = language_block.find('span', class_='color-fg-default text-bold mr-1').text.strip()
            if language == 'Other':
                percentage = language_block.find_all('span')[0].text.strip().split('\n')[-1].strip().replace('%', '')
            else:
                percentage = language_block.find_all('span')[1].text.strip().replace('%', '')
            languages[language] = percentage
            print(f'[INFO] processing {url}')

        return {
            "url": url,
            "extra": {
                "owner": owner,
                "language_stats": languages
            }
        }

    async def search_github(self):
        async with aiohttp.ClientSession() as session:
            all_repo_links = []
            for base_url in self.base_urls:
                html = await self.make_request(session, base_url)
                if not html:
                    logging.warning(f"No HTML response for base URL: {base_url}")
                    continue

                soup = BeautifulSoup(html, 'html.parser')
                for div in soup.find_all('div', class_='Box-sc-g0xbh4-0 MHoGG search-title'):
                    link = div.find('a')
                    href = link['href']
                    if href.startswith('/'):
                        all_repo_links.append(f"https://github.com{href}")
                    else:
                        logging.warning(f"Invalid link format, skipped: {href} -- {base_url}")

            return list(set(all_repo_links))

    async def run(self):
        repo_data = []
        async with aiohttp.ClientSession() as session:
            repo_links = await self.search_github()
            for url in repo_links:
                data = await self.extract_repo_data(session, url)
                if data:
                    repo_data.append(data)
                else:
                    logging.error(f"Failed to extract data for URL: {url}")

        return repo_data


def read_input_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)


def write_output_to_file(output_data, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(output_data, file, indent=4)
        logging.info(f"Output saved to '{file_path}'")


async def main():
    input_data = read_input_from_file('data/input_data.json')
    crawler = GitHubCrawler(
        keywords=input_data['keywords'],
        proxies=input_data['proxies'],
        search_type=input_data['type']
    )
    result = await crawler.run()
    write_output_to_file(result, 'data/output_data.json')
    logging.info("Results saved to 'output_data.json'")


if __name__ == "__main__":
    asyncio.run(main())
