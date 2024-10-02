# GitHub Crawler

This project is a parser for GitHub, allowing you to search for and extract data about repositories based on specified keywords.

## Installation

### Prerequisites

Ensure you have the following tools installed:

- [Python](https://www.python.org/downloads/) (version 3.7 or higher)
- [Poetry](https://python-poetry.org/docs/#installation)

### Cloning the Repository

First, clone the repository:

```
git clone https://github.com/codeberrypro/github_scraper.git
cd github_scraper
```

## Installing Dependencies

Use [Poetry](https://python-poetry.org/) to install the dependencies:

```bash
poetry install
```

## Proxy Configuration

The project includes files for storing proxy credentials. To properly configure and use the proxies, follow these steps:

1. Locate the `.env` file in the project directory.
2. Add your proxy password and login to the `.env` file in the following format:

    ```makefile
    PROXY_PASSWORD=your_password
    PROXY_LOGIN=your_login
    ```

3. Locate the `input_data.json` file in the project directory.
4. Add your proxy credentials to the `input_data.json` file in the following format:


## Usage

To run the crawler, execute the following command:

```bash
poetry run python main.py
 ```

## Input Data Format

Your `input_data.json` file should be structured as follows:

```json
{
    "keywords": ["keyword1", "keyword2"],
    "proxies": ["proxy1", "proxy2"],
    "type": "repositories"
}

