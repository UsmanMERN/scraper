import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin

class WebScraper:
    def __init__(self, url):
        self.url = url
        self.soup = self.get_soup()

    def get_soup(self):
        """Fetch and parse the webpage."""
        try:
            response = requests.get(self.url)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'lxml')
        except requests.exceptions.RequestException as e:
            print(f"Error fetching the URL: {e}")
            return None

    def extract_emails(self):
        """Extract all email addresses from the page."""
        if not self.soup:
            return []
        email_regex = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
        emails = re.findall(email_regex, self.soup.get_text())
        return list(set(emails))

    def extract_phone_numbers(self):
        """Extract phone numbers from the page."""
        if not self.soup:
            return []
        phone_regex = r"\+?\d[\d -]{8,12}\d"
        phones = re.findall(phone_regex, self.soup.get_text())
        return list(set(phones))

    def extract_social_links(self):
        """Extract social media links."""
        if not self.soup:
            return []
        social_platforms = ["facebook", "twitter", "linkedin", "instagram", "youtube"]
        social_links = set()
        for link in self.soup.find_all('a', href=True):
            href = link['href']
            for platform in social_platforms:
                if platform in href:
                    social_links.add(urljoin(self.url, href))
        return list(social_links)

    def extract_meta_info(self):
        """Extract meta information from the page."""
        if not self.soup:
            return {}
        meta_info = {}
        meta_tags = self.soup.find_all('meta')
        for tag in meta_tags:
            if 'name' in tag.attrs and 'content' in tag.attrs:
                meta_info[tag['name']] = tag['content']
        return meta_info

    def extract_main_content(self):
        """Extract main content from common content containers."""
        if not self.soup:
            return []
        content_containers = self.soup.find_all(['article', 'main', 'div'], 
                                              class_=re.compile(r'content|article|post|main'))
        return [container.get_text(strip=True) for container in content_containers]

    def extract_headers(self):
        """Extract all headers from the page."""
        if not self.soup:
            return {}
        headers = {}
        for i in range(1, 7):
            headers[f'h{i}'] = [h.get_text(strip=True) 
                              for h in self.soup.find_all(f'h{i}')]
        return headers

    def extract_images(self):
        """Extract all image URLs and their alt text."""
        if not self.soup:
            return []
        images = []
        for img in self.soup.find_all('img'):
            image_info = {
                'src': urljoin(self.url, img.get('src', '')),
                'alt': img.get('alt', ''),
                'title': img.get('title', '')
            }
            images.append(image_info)
        return images

    def extract_links(self):
        """Extract all links from the page."""
        if not self.soup:
            return []
        links = []
        for link in self.soup.find_all('a', href=True):
            href = link['href']
            if href.startswith(('http', 'https', '/')):
                links.append({
                    'url': urljoin(self.url, href),
                    'text': link.get_text(strip=True)
                })
        return links

    def extract_contact_info(self):
        """Extract contact information including addresses."""
        if not self.soup:
            return {}
        # Common address patterns
        address_regex = r'\d+\s+[A-Za-z0-9\s,.-]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr)[,\s]+(?:[A-Za-z\s]+)[,\s]+(?:[A-Z]{2})\s+\d{5}'
        addresses = re.findall(address_regex, self.soup.get_text())
        
        return {
            'addresses': list(set(addresses)),
            'emails': self.extract_emails(),
            'phones': self.extract_phone_numbers()
        }

    def extract_all_data(self):
        """Extract all available data from the webpage."""
        return {
            "url": self.url,
            "meta_info": self.extract_meta_info(),
            "headers": self.extract_headers(),
            "main_content": self.extract_main_content(),
            "contact_info": self.extract_contact_info(),
            "social_links": self.extract_social_links(),
            "images": self.extract_images(),
            "links": self.extract_links()
        }