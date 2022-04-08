"""
Script that was used for webscraping the tabs data
"""
from enum import IntEnum
from selenium import webdriver
from bs4 import BeautifulSoup
import time
import os

from selenium.webdriver.common.by import By


def auto_str(cls):
    def __str__(self):
        return f"{type(self).__name__}:{', '.join('%s=%s' % item for item in vars(self).items())}"

    cls.__str__ = __str__
    return cls

@auto_str
class FilterItem(dict):
    def __init__(self, a_element):
        first_span = a_element.findAll('span')[0]
        href = a_element['href']

        self.code = a_element['value']
        self.name = first_span.text
        self.filter_pattern = "blank" #href[href.index('&&'):]

    def to_dictionary(self):
        return {"code": self.code, "name": self.name, "pattern": self.filter_pattern}

def print_list(list):
    return [str(x) for x in list]


class FilterType(IntEnum):
    GENRE = 0
    STYLE = 1
    DECADE = 2


class SingleFilterExtractor:
    PAGE_URL = "https://www.ultimate-guitar.com/explore?type[]=Tabs"
    driver = None

    def __init__(self):
        self.set_chrome_driver()

    def get_song_links(self):
        """
        This grabs all song links under tabs section and returns the links
        :return:
        """
        song_links = []

        pages = 100
        for i in range(pages):
            paginator = self.PAGE_URL + "&page=" + str(i+1)
            self.driver.get(paginator)
            print("Currently looking up: {}".format(paginator))

            time.sleep(5)

            s = self.driver.find_elements(by=By.TAG_NAME, value="article")
            x = s[-1].get_attribute("innerHTML")

            soup = BeautifulSoup(x, 'html.parser')

            for i in soup.find_all("a"):
                link = i.get("href")
                if link.split(".")[0] == "https://tabs":  # Select only tabs
                    #print(link)
                    song_links.append(link)

        return song_links


    def extract_tab(self, link):
        print("Currently extracting: {}".format(link))
        self.driver.get(link)

        time.sleep(5)

        # Make sure TAB is in standard tuning
        spec = self.driver.find_elements(by=By.ID, value="tuning")
        for i in spec:
            field = i.get_attribute("innerHTML")
            if str(field) != "E A D G B E":
                print("Tab not in standard tuning, skipping")
                continue

        # Prepare file to write to
        try:
            link_list = link.split("/")[-2::]
            filename = "_".join(link_list) + ".txt"
            f = open("data/tabs/"+filename, "w")

            s = self.driver.find_elements(by=By.CLASS_NAME, value="_2jIGi")
            for i, v in enumerate(s):
                elem = v.get_attribute("innerHTML")
                #print("Element: {}".format(v))
                soup = BeautifulSoup(elem, "html.parser")
                x = soup.find_all("span")

                tab = []
                tab_encoded = []
                for i in x:
                    sliced = i.text.split("|")
                    if len(sliced) == 1:  # ignore if it's not the notes tabs
                        continue
                    if sliced[1][0] != "-": # if it doesn't begin with -, continue
                        continue

                    tab.append(i.text)
                    f.write(i.text.strip("\n"))
                f.write("\n\n")
        except Exception as e:
            print("Error occured")
            return e
        finally:
            f.close() # close the file




    def set_chrome_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--incognito')
        options.add_argument('--headless')
        cwd = os.getcwd()
        print(cwd)
        self.driver = webdriver.Chrome("gather/chromedriver", options=options)


    def close_chrome_driver(self):
        self.driver.close()

if __name__ == '__main__':
    extractor = SingleFilterExtractor()

    try:
        links = extractor.get_song_links()

        for link in links:
            try:
                extractor.extract_tab(link) # link
            except:
                print("error occured while processing tab, removing file")

                link_list = link.split("/")[-2::]
                filename = "_".join(link_list) + ".dat"
                file_path = "../data/tabs/"+filename
                if os.path.exists(file_path):
                    os.remove(file_path)


    except Exception as inst:
        print(inst)
        extractor.close_chrome_driver()


    extractor.close_chrome_driver()
