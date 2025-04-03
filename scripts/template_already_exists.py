#!/usr/bin/env python3

import argparse
import requests
from typing import Tuple
from bs4 import BeautifulSoup as bs

def check_template_exists(template_name: str) -> Tuple[bool, str]:
    """
    Check if a template already exists on the Community Apps store page.
    :param template_name: The name of the template to check.
    :return: True if the template exists, False otherwise.
    """
    url = f"https://unraid.net/community/apps?q={template_name}#r"
    response = requests.get(url)

    # If no response, return False
    if not response:
        return False, url

    # Check if response HTML has at least one "article" element with a "h3" element containing the template name in it
    soup: bs4.BeautifulSoup = bs(response.content, 'html.parser')
    articles = soup.find_all("article")

    # If no articles, return False
    if not articles:
        return False, url

    # Check if any article has a h3 element with the template name in it
    for article in articles:
        # Check if the article has a h3 element
        h3 = article.find("h3")
        if not h3:
            continue

        # Check if the template name is in the h3 element
        if template_name.lower() in h3.text.lower():
            return True, url

    # If no article has the template name in it, return False
    return False, url

if __name__ == "__main__":
    args = argparse.ArgumentParser(description="Check if a template already exists on the Community Apps store page.")
    args.add_argument("template_name", type=str, help="The name of the template to check.")
    args = args.parse_args()

    # Check if the template already exists
    exists, url = check_template_exists(args.template_name)

    print(f"{url}\n")

    if exists:
        print(f"TRUE. The template '{args.template_name}' already exists.")
    else:
        print(f"FALSE. The template '{args.template_name}' does not exist.")
