import re

import PyPublicaties
from bs4 import BeautifulSoup
import requests

from utils.parse import html_to_md

#  Disable SSL warnings for requests
import urllib3
urllib3.disable_warnings()



def get_obm_document_info(identifier):
    """
    Retrieves document data from the officielebekendmakingen.nl API
    """

    results = PyPublicaties.retrieve_publications(
        query_list=[
            f'dt.identifier={identifier}',
        ],
        max_records=1,
    )

    # find the result where the identifier is the same as the document's identifier
    result = next((r for r in results if r.identifier[0] == identifier), None)
    if result is None:
        raise ValueError(f"Result with identifier {identifier} not found.")


    # Retrieve metadata from the document
    title = result.title[0]
    date = result.date[0]
    doc_type = result.type[0]


    # Retrieve the html content
    try:
        # Try to retrieve the HTML content from the cache
        html_content = get_obm_html(identifier)
    except ValueError as e:
        # print the error and move on
        print(f"Error retrieving HTML content for {identifier}: {e}")

    if not html_content:
        # Try to retrieve the HTML content from the base identifier
        # (remove -b[0-9]+ from the identifier)
        base_identifier = re.sub(r'-b[0-9]+$', '', identifier)
        html_content = get_obm_html(base_identifier) # Accept the raised error if it occurs

    # Check if the HTML content is empty
    if not html_content:
        raise ValueError(f"HTML content not found for {identifier}.")

    # Parse to markdown
    md_content = html_to_md(html_content)

    return {
        'identifier': identifier,
        'title': title,
        'date': date,
        'html_content': html_content,
        'md_content': md_content,
        'type': doc_type,
    }


def get_obm_html(identifier):
    """
    Retrieves the HTML content of a document from the officielebekendmakingen.nl API
    """
    # Retrieve the html content
    html = requests.get(f"https://zoek.officielebekendmakingen.nl/{identifier}.html", verify=False)
    soup = BeautifulSoup(html.content, "html.parser")

    # Check if there is a web-version available (#content .alert contains text: 'niet beschikbaar als Webversie)
    alert = soup.find(id="content").find("div", class_="alert")
    if alert is not None and "niet beschikbaar als Webversie" in alert.get_text():
        raise ValueError(f"[web] Web version not available for {identifier}.")


    # Find the first <article> tag inside #content
    article = soup.find(id="content").find("article")
    if article is None:
        raise ValueError(f"[article] Article tag not found in HTML content for {identifier}.")

    # Remove all links from the article, but keep the text
    # This is to prevent the links from being converted to markdown links
    for a in article.find_all("a"):
        a.replace_with(a.get_text())

    return str(article)
