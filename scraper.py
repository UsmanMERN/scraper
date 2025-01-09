# scraper.py
from bs4 import BeautifulSoup
import requests
import re
from urllib.parse import urljoin
import json
from datetime import datetime

class WebScraper:
    def __init__(self, url, scrape_type="general"):
        self.url = url
        self.scrape_type = scrape_type
        self.soup = self.get_soup()
        
        # Common product selectors for major e-commerce sites
        self.product_selectors = {
            "amazon": {
                "price": "#priceblock_ourprice, .a-price-whole",
                "title": "#productTitle",
                "rating": "#acrPopover",
                "reviews": "#acrCustomerReviewText",
                "availability": "#availability span"
            },
            "ebay": {
                "price": ".x-price-primary",
                "title": ".x-item-title",
                "rating": ".stars-ratings",
                "reviews": ".review-ratings-count",
                "availability": ".quantity-available"
            },
            "daraz": {
                "price": ".pdp-price",
                "title": ".pdp-mod-product-badge-title",
                "rating": ".score",
                "reviews": ".count",
                "availability": ".stock",
                "image_url": ".gallery-preview-panel__image",
                "seller": ".pdp-product-brand a",
                "specifications": ".specification-keys li"
            },
            # Add more e-commerce sites as needed
        }

    def get_soup(self):
        """Fetch and parse the webpage with rotating user agents."""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        }
        try:
            response = requests.get(self.url, headers=headers, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'lxml')
        except requests.exceptions.RequestException as e:
            print(f"Error fetching the URL: {e}")
            return None

    def extract_product_data(self):
        """Extract product-specific data from e-commerce sites."""
        if not self.soup:
            return {}

        product_data = {
            "url": self.url,
            "timestamp": datetime.now().isoformat(),
            "products": []
        }

        # Determine the site based on the URL
        site = None
        if "amazon" in self.url:
            site = "amazon"
        elif "ebay" in self.url:
            site = "ebay"
        elif "daraz" in self.url:
            site = "daraz"

        # Use site-specific selectors if available
        if site and site in self.product_selectors:
            selectors = self.product_selectors[site]
            product_info = {
                "title": self._extract_text(self.soup, selectors["title"]),
                "price": self._extract_price(self.soup, selectors["price"]),
                "currency": self._detect_currency(self.soup, selectors["price"]),
                "rating": self._extract_rating(self.soup, selectors["rating"]),
                "reviews_count": self._extract_reviews_count(self.soup, selectors["reviews"]),
                "availability": self._extract_availability(self.soup, selectors["availability"]),
                "image_url": self._extract_image(self.soup, selectors["image_url"]),
                "seller": self._extract_seller(self.soup, selectors["seller"]),
                "specifications": self._extract_specifications(self.soup, selectors["specifications"])
            }
            if product_info["title"] and product_info["price"]:
                product_data["products"].append(product_info)
        else:
            # Generic product extraction
            products = self.soup.find_all(class_=re.compile(r'product|item|listing'))
            for product in products:
                product_info = {
                    "title": self._extract_text(product, '.product-title, .item-title, h2, h3'),
                    "price": self._extract_price(product),
                    "currency": self._detect_currency(product),
                    "rating": self._extract_rating(product),
                    "reviews_count": self._extract_reviews_count(product),
                    "availability": self._extract_availability(product),
                    "image_url": self._extract_image(product),
                    "seller": self._extract_seller(product),
                    "specifications": self._extract_specifications(product)
                }
                if product_info["title"] and product_info["price"]:
                    product_data["products"].append(product_info)

        return product_data

    def _extract_text(self, element, selector, default=""):
        """Helper method to extract text from elements."""
        try:
            found = element.select_one(selector)
            return found.get_text(strip=True) if found else default
        except:
            return default

    def _extract_price(self, element, selector=None):
        """Extract and normalize price."""
        price_text = self._extract_text(element, selector or '.price, .product-price, [class*="price"]')
        if price_text:
            # Remove currency symbols and normalize
            price = re.sub(r'[^\d.,]', '', price_text)
            try:
                return float(price.replace(',', '.'))
            except:
                return None
        return None

    def _detect_currency(self, element, selector=None):
        """Detect currency symbol/code."""
        price_text = self._extract_text(element, selector or '.price, .product-price, [class*="price"]')
        currency_match = re.search(r'[\$\€\£\¥]|USD|EUR|GBP|JPY', price_text)
        return currency_match.group() if currency_match else None

    def _extract_rating(self, element, selector=None):
        """Extract product rating."""
        rating_text = self._extract_text(element, selector or '.rating, .stars, [class*="rating"]')
        try:
            return float(re.search(r'\d+\.?\d*', rating_text).group())
        except:
            return None

    def _extract_reviews_count(self, element, selector=None):
        """Extract number of reviews."""
        reviews_text = self._extract_text(element, selector or '.reviews-count, [class*="review"]')
        try:
            return int(re.search(r'\d+', reviews_text).group())
        except:
            return 0

    def _extract_availability(self, element, selector=None):
        """Extract product availability status."""
        return self._extract_text(element, selector or '.availability, .stock-status, [class*="stock"]')

    def _extract_image(self, element, selector=None):
        """Extract product image URL."""
        img = element.select_one(selector or 'img')
        return urljoin(self.url, img['src']) if img and 'src' in img.attrs else None

    def _extract_seller(self, element, selector=None):
        """Extract seller information."""
        return self._extract_text(element, selector or '.seller, .vendor, [class*="seller"]')

    def _extract_specifications(self, element, selector=None):
        """Extract product specifications."""
        specs = {}
        spec_elements = element.select(selector or '.specifications li, .specs li, .details li')
        for spec in spec_elements:
            text = spec.get_text(strip=True)
            if ':' in text:
                key, value = text.split(':', 1)
                specs[key.strip()] = value.strip()
        return specs

    def extract_all_data(self):
        """Extract all data based on scrape type."""
        if self.scrape_type == "products":
            return self.extract_product_data()
        else:
            # Original general scraping logic
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

    def track_price(self, product_url, target_price):
        """Track the price of a product and notify if it drops below the target price."""
        self.url = product_url
        self.soup = self.get_soup()
        product_data = self.extract_product_data()
        if product_data["products"]:
            current_price = product_data["products"][0]["price"]
            if current_price and current_price <= target_price:
                return f"Price dropped to {current_price} for {product_data['products'][0]['title']}"
            else:
                return f"Current price is {current_price} for {product_data['products'][0]['title']}"
        return "Product data could not be extracted."

    def compare_prices(self, product_urls):
        """Compare prices of the same product across different URLs."""
        price_comparison = {}
        for url in product_urls:
            self.url = url
            self.soup = self.get_soup()
            product_data = self.extract_product_data()
            if product_data["products"]:
                price_comparison[url] = product_data["products"][0]["price"]
        return price_comparison

    def extract_meta_info(self):
        """Extract meta information from the webpage."""
        meta_info = {}
        if self.soup:
            for meta in self.soup.find_all('meta'):
                if 'name' in meta.attrs:
                    meta_info[meta.attrs['name']] = meta.attrs.get('content', '')
                elif 'property' in meta.attrs:
                    meta_info[meta.attrs['property']] = meta.attrs.get('content', '')
        return meta_info

    def extract_headers(self):
        """Extract headers (h1, h2, h3, etc.) from the webpage."""
        headers = {}
        if self.soup:
            for i in range(1, 7):
                headers[f'h{i}'] = [h.get_text(strip=True) for h in self.soup.find_all(f'h{i}')]
        return headers

    def extract_main_content(self):
        """Extract the main content of the webpage."""
        if self.soup:
            return self.soup.get_text(strip=True)
        return ""

    def extract_contact_info(self):
        """Extract contact information from the webpage."""
        contact_info = {}
        if self.soup:
            # Example: Extract email addresses
            emails = re.findall(r'[\w\.-]+@[\w\.-]+', self.soup.get_text())
            if emails:
                contact_info['emails'] = emails
            # Example: Extract phone numbers
            phones = re.findall(r'\+?\d[\d -]{8,12}\d', self.soup.get_text())
            if phones:
                contact_info['phones'] = phones
        return contact_info

    def extract_social_links(self):
        """Extract social media links from the webpage."""
        social_links = {}
        if self.soup:
            social_platforms = ['facebook', 'twitter', 'instagram', 'linkedin', 'youtube']
            for platform in social_platforms:
                links = self.soup.find_all('a', href=re.compile(platform, re.IGNORECASE))
                if links:
                    social_links[platform] = [link['href'] for link in links]
        return social_links

    def extract_images(self):
        """Extract all image URLs from the webpage."""
        images = []
        if self.soup:
            for img in self.soup.find_all('img'):
                if 'src' in img.attrs:
                    images.append(urljoin(self.url, img['src']))
        return images

    def extract_links(self):
        """Extract all links from the webpage."""
        links = []
        if self.soup:
            for a in self.soup.find_all('a', href=True):
                links.append(urljoin(self.url, a['href']))
        return links

# Example usage:
# scraper = WebScraper("https://www.daraz.pk/products/t900-8-t900-209-t900-i507409182-s2745188844.html", scrape_type="products")
# print(scraper.extract_product_data())