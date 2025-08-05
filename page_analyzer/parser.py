from bs4 import BeautifulSoup
import requests


def get_url_elems(url):
    response = requests.get(url, timeout=5)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    h1 = soup.h1.string if soup.h1 else ''
    title = soup.title.string if soup.title else ''
    description_tag = soup.find('meta', attrs={'name': 'description'})
    description = description_tag['content'] if description_tag and 'content' in description_tag.attrs else ''  # noqa: E501
    code = response.status_code
    return h1, title, description, code
