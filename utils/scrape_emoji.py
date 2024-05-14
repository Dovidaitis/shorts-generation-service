from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from typing import List
from math import ceil
import time
import re
import requests
import os


class BrowserEmulator:
    @staticmethod
    def configure_options(headless: bool = False) -> Options:
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")  # Enable headless mode
        return chrome_options

    def __init__(self, headless: bool = False):
        options = BrowserEmulator.configure_options(headless=headless)
        self.driver = webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()), options=options
        )
        self.WAIT_TIME = 5  # seconds

    def click_element(self, selector_type: str, selector_value: str) -> None:
        """
        Clicks an element based on the selector type
        (e.g., 'id', 'class_name', 'xpath', 'css_selector')
        and the selector value.
        """
        wait = WebDriverWait(self.driver, self.WAIT_TIME)
        by_type = self._get_by_type(selector_type)
        element = wait.until(EC.element_to_be_clickable((by_type, selector_value)))
        element.click()

    def check_parent_html(self, selector_type: str, selector_value: str) -> str:
        """
        Returns html of parents from a child's perspective
        (e.g., 'id', 'class_name', 'xpath', 'css_selector')
        and the selector value.
        """
        wait = WebDriverWait(self.driver, self.WAIT_TIME)
        by_type = self._get_by_type(selector_type)
        try:
            element = wait.until(EC.element_to_be_clickable((by_type, selector_value)))
            return element.get_attribute("outerHTML")
        except NoSuchElementException:
            return ""

    def _get_by_type(self, selector_type: str):
        """
        Maps a human-readable selector type to the corresponding Selenium By type.
        """
        selector_map = {
            "id": By.ID,
            "class_name": By.CLASS_NAME,
            "xpath": By.XPATH,
            "css_selector": By.CSS_SELECTOR,
            "name": By.NAME,
            "tag_name": By.TAG_NAME,
            "link_text": By.LINK_TEXT,
            "partial_link_text": By.PARTIAL_LINK_TEXT,
        }
        return selector_map.get(
            selector_type.lower(), By.XPATH
        )  # Default to XPATH if not found

    @staticmethod
    def create_area_label_xpath(aria_label: str) -> str:
        return f'//*[@aria-label="{aria_label}"]'

    @staticmethod
    def crete_area_label_ancestors_xpath(aria_label: str) -> str:
        return f'//*[@aria-label="{aria_label}"]/ancestor::*'

    def check_parent_html_by_aria_label(self, aria_label: str) -> str:
        try:
            wait = WebDriverWait(self.driver, self.WAIT_TIME)
            xpath = self.crete_area_label_ancestors_xpath(aria_label)
            element = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
            return element.get_attribute("outerHTML")
        except NoSuchElementException:
            print("***")
            return ""


class BrowserNavigator(BrowserEmulator):
    def __init__(self, headless: bool = True):
        super().__init__(headless=headless)
        self.tags_to_remove = [
            "script",
            "style",
            "noscript",
            "iframe",
            "img",
            "link",
            "meta",
            "title",
            "picture",
            "ul",
            "li",
        ]
        self.clickable_tags = ["a", "button", "input", "label", "div", "span", "p"]

    @staticmethod
    def remove_closing_tags(html_content: str) -> str:
        pattern = r"</[^>]*>"
        return re.sub(pattern, "", html_content)

    def remove_tags(
        self, html_content: str, tags_to_remove: List[str]
    ) -> BeautifulSoup:
        """
        Provide a list of tags that will be removed from the html content.
        It will return a BeautifulSoup object.
        """
        soup = BeautifulSoup(html_content, "lxml")
        for tag in tags_to_remove:
            for match in soup.find_all(tag):
                match.decompose()

        return soup

    def retain_tags(
        self, html_content: str, tags_to_retain: List[str]
    ) -> BeautifulSoup:
        """
        Retains only the specified tags in the html content, removing all other tags.
        It will return a BeautifulSoup object with only the specified tags.
        STILL WIP
        """
        soup = BeautifulSoup(html_content, "lxml")

        all_tags = {tag.name for tag in soup.find_all()}

        tags_to_remove = all_tags - set(tags_to_retain)
        print(" .         -> BEFORE:")
        self.psoup(soup)

        for tag in tags_to_remove:
            for match in soup.find_all(tag):
                match.decompose()

        print(" .         -> AFTER:")
        self.psoup(soup)

        return soup

    @staticmethod
    def psoup(soup: BeautifulSoup, minify: bool = False) -> None:
        if minify:
            print(BrowserNavigator.remove_closing_tags(soup.prettify()))
        else:
            print(soup.prettify())

    @staticmethod
    def str_soup(soup: BeautifulSoup, minify: bool = False) -> str:
        if minify:
            return BrowserNavigator.remove_closing_tags(soup.prettify())
        else:
            return soup.prettify()

    @staticmethod
    def get_all_hrefs(html: str) -> List[str]:
        soup = BeautifulSoup(html, 'lxml')
        a_tags = soup.find_all('a')
        hrefs = [tag.get('href') for tag in a_tags]
        cleaned_hrefs = [href for href in hrefs if href and "/apple/ios-17.4/" in href]
        return cleaned_hrefs

    @staticmethod
    def get_all_img_srcs(html: str) -> List[str]:
        soup = BeautifulSoup(html, 'lxml')
        img_tags = soup.find_all('img')
        srcs = [tag.get('src') for tag in img_tags if "apple" in tag.get('src') and ".png" in tag.get('src')]
        print(srcs)
        return srcs



def get_links():
    hrefs = []
    bn = BrowserNavigator(headless=False)
    bn.driver.get("https://emojipedia.org/apple")
    bn.driver.maximize_window()

    input("When you're ready, press Enter to continue...")

    total_height = bn.driver.execute_script("return document.body.scrollHeight;")
    viewport_height = bn.driver.execute_script("return window.innerHeight;")
    scrolls_needed = ceil(total_height / viewport_height)

    # Scroll down one screen at a time
    for _ in range(scrolls_needed):
        hrefs.append(bn.get_all_hrefs(bn.driver.page_source))
        bn.driver.execute_script("window.scrollBy(0, window.innerHeight);")
        time.sleep(1)

    unique = set()
    for links in hrefs:
        for link in links:
            if "skin-tone" not in link:
                print(f"Adding -> {link}")
                unique.add(link)
        
    return unique

def download_emoji_image(postfix: str, bn: BrowserNavigator):
    URL = f"https://emojipedia.org{postfix}"
    current_files = os.listdir("assets/ios_emoji")

    bn.driver.get(URL)
    srcs = bn.get_all_img_srcs(bn.driver.page_source)
    for src in srcs:
        name = src.split("/")[-1]
        if name in current_files:
            print(f" >> Skipping {name} as it already exists.")
            continue
        full_path = f"assets/ios_emoji/{name}"
        response = requests.get(src)

        if response.status_code == 200:
            with open(full_path, "wb") as file:
                file.write(response.content)
            print(f" >> Image {name} downloaded successfully.")
        else:
            print(f" >> Failed {name} to download image.")



        
if __name__ == "__main__":
    unique = get_links()
    print(f"Unique links: {len(unique)}")
    input("Press Enter to continue...")
    bn = BrowserNavigator(headless=True)
    for uni in unique:
        print(f"Accessing {uni}")
        download_emoji_image(uni, bn)

