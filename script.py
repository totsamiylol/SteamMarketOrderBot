from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
import keyboard
from selenium.webdriver.common.by import By
import requests
from bs4 import BeautifulSoup
import time
import json
import asyncio
import aiohttp

import database
import user_data

from item_class import Item, SkinItem

request_counter = 0

rarity_dict = {
    'tag_Rarity_Common_Weapon': 'Consumer Grade',
    'tag_Rarity_Uncommon_Weapon': 'Industrial Grade',
    'tag_Rarity_Rare_Weapon': 'Mil-Spec Grade',
    'tag_Rarity_Rare': 'Mil-Spec Grade',
    'tag_Rarity_Rare_Character': 'Mil-Spec Grade',
    'tag_Rarity_Mythical_Weapon': 'Restricted',
    'tag_Rarity_Mythical': 'Restricted',
    'tag_Rarity_Mythical_Character': 'Restricted',
    'tag_Rarity_Legendary_Weapon': 'Classified',
    'tag_Rarity_Legendary': 'Classified',
    'tag_Rarity_Legendary_Character': 'Classified',
    'tag_Rarity_Ancient_Weapon': 'Covert',
    'tag_Rarity_Ancient': 'Covert',
    'tag_Rarity_Ancient_Character': 'Covert'
}

wear_dict = {
    "tag_WearCategory0": "Factory New",
    "tag_WearCategory1": "Minimal Wear",
    "tag_WearCategory2": "Field-Tested",
    "tag_WearCategory3": "Well-Worn",
    "tag_WearCategory4": "Battle-Scarred"
}

class Collection:
    def __init__(self, collection_type, collection_name):
        self.collection_type = collection_type
        self.collection_name = collection_name
        if self.collection_type == "Patches":
            self.links = {"tag_Rarity_Rare": [], "tag_Rarity_Mythical": [], "tag_Rarity_Legendary": [],
                          "tag_Rarity_Ancient": []}
        elif self.collection_type == "Stickers":
            self.links = {"tag_Rarity_Rare": [], "tag_Rarity_Mythical": [], "tag_Rarity_Legendary": [],
                          "tag_Rarity_Ancient": []}
        elif self.collection_type == "Agents":
            self.links = {"tag_Rarity_Rare_Character": [], "tag_Rarity_Mythical_Character": [],
                          "tag_Rarity_Legendary_Character": [], "tag_Rarity_Ancient_Character": []}

    def parse_collection(self):
        global request_counter
        filter_links = []

        for rarity in self.links.keys():
            filter_link = generate_filter_url(self.collection_type, self.collection_name, rarity)
            filter_links.append({"rarity": rarity, "item_type": self.collection_type, "link": filter_link})

        all_links = asyncio.run(parse_all_filters(filter_links))
        print()
        request_counter += len(all_links)

        # adding item links to collection object
        for link in all_links:
            self.links[link['rarity']].append(link['links'])

    def get_all_items(self):
        account_id = profile_ids[account_no]
        self.parse_collection()
        items = []
        for rarity in self.links.keys():
            for link in self.links[rarity]:
                data = database.get_data(account_id=account_id, type_=self.collection_type, rarity=rarity_dict[rarity])
                if data is None:
                    continue
                items.append(Item(self.collection_type, rarity,  data[5], data[6], self.collection_name, link))
        return items

class SkinCollection:
    wear = {"tag_WearCategory0": "%28Factory%20New%29", "tag_WearCategory1": "%28Minimal%20Wear%29",
            "tag_WearCategory2": "%28Field-Tested%29", "tag_WearCategory3": "%28Well-Worn%29",
            "tag_WearCategory4": "%28Battle-Scarred%29"}
    number_of_positions = {
        "op_coll": {
            "tag_Rarity_Common_Weapon": 5,
            "tag_Rarity_Uncommon_Weapon": 4,
            "tag_Rarity_Rare_Weapon": 4,
            "tag_Rarity_Mythical_Weapon": 3,
            "tag_Rarity_Legendary_Weapon": 2,
            "tag_Rarity_Ancient_Weapon": 1
        },
        "com_coll": {
            "tag_Rarity_Rare_Weapon": 7,
            "tag_Rarity_Mythical_Weapon": 5,
            "tag_Rarity_Legendary_Weapon": 3,
            "tag_Rarity_Ancient_Weapon": 2
        }
    }

    def parse_collection(self):
        global request_counter
        filter_links = []
        for rarity in self.nonFullLinks_by_rarities:
            link = generate_filter_url("skin", self.collection, rarity, wear="tag_WearCategory2", stat_track=False)
            if self.is_operation:
                if len(self.nonFullLinks_by_rarities[rarity]) < self.number_of_positions["op_coll"][rarity]:
                    filter_links.append({"rarity": rarity, "link": link, "item_type": "operation_skin"})
            else:
                if len(self.nonFullLinks_by_rarities[rarity]) < self.number_of_positions["com_coll"][rarity]:
                    filter_links.append({"rarity": rarity, "link": link, "item_type": "community_skin"})

        all_links = asyncio.run(parse_all_filters(filter_links))
        print()
        request_counter += len(all_links)

        for links_rarity in all_links:
            for link in links_rarity["links"]:
                not_full_link = link.split("%28")[0]
                rarity = links_rarity["rarity"]
                if not_full_link not in self.nonFullLinks_by_rarities[rarity]:
                    self.nonFullLinks_by_rarities[rarity].append(not_full_link)

    def __init__(self, collection):
        self.collection = collection
        self.is_operation = True if collection.find("community") == -1 else False
        if self.is_operation:
            self.nonFullLinks_by_rarities = {"tag_Rarity_Common_Weapon": [], "tag_Rarity_Uncommon_Weapon": [],
                                             "tag_Rarity_Rare_Weapon": [], "tag_Rarity_Mythical_Weapon": [],
                                             "tag_Rarity_Legendary_Weapon": [], "tag_Rarity_Ancient_Weapon": []}
        else:
            self.nonFullLinks_by_rarities = {"tag_Rarity_Rare_Weapon": [], "tag_Rarity_Mythical_Weapon": [],
                                             "tag_Rarity_Legendary_Weapon": [], "tag_Rarity_Ancient_Weapon": []}

    def get_all_items(self):
        account_id = profile_ids[account_no]
        self.parse_collection()
        items = []
        for rarity, links in self.nonFullLinks_by_rarities.items():
            for link in links:
                for wear in self.wear:
                    ind = link.rfind("/")
                    if self.is_operation:
                        data = database.get_data(type_="Op Skins", rarity=rarity_dict[rarity], wear=wear_dict[wear], account_id=account_id)
                        if data is not None:
                            res_link = link[:ind] + "/" + link[ind + 1:] + self.wear[wear]
                            items.append(SkinItem("Op Skins", self.is_operation, rarity, collection=self.collection,
                                                  price=data[5], quantity=data[6], link=res_link, wear=wear,
                                                  stat_trak=None))
                    else:
                        res_link1 = link[:ind] + "/" + link[ind + 1:] + self.wear[wear]
                        res_link2 = link[:ind] + "/StatTrak%E2%84%A2%20" + link[ind + 1:] + self.wear[wear]
                        data1 = database.get_data(type_="Case Skins", rarity=rarity_dict[rarity], wear=wear_dict[wear], stat_trak="No", account_id=account_id)
                        if data1 is not None:
                            items.append(SkinItem("Case Skins", self.is_operation, rarity, collection=self.collection,
                                                  price=data1[5], quantity=data1[6], link=res_link1, wear=wear,
                                                  stat_trak=False))
                        data2 = database.get_data(type_="Case Skins", rarity=rarity_dict[rarity], wear=wear_dict[wear], stat_trak="Yes", account_id=account_id)
                        if data2 is not None:
                            items.append(SkinItem("Case Skins", self.is_operation, rarity, collection=self.collection,
                                                  price=data2[5], quantity=data2[6], link=res_link2, wear=wear,
                                                  stat_trak=True))
        return items

def place_order(driver, item_type, price, quantity):
    global current_proxy
    try:
        if driver.find_element(By.CLASS_NAME, "error_ctn"): # <------ ERROR HERE -------------------------------------------------------------
            change_profile(current_proxy + 1, driver)
            current_proxy = (current_proxy + 1) % 10
            return place_order(driver, item_type, price, quantity)
    except NoSuchElementException:
        pass
    try:
        if item_type in ["Agents", "Case Skins", "Op Skins"]:
            driver.find_element(By.CLASS_NAME, 'market_noncommodity_buyorder_button').click()
        else:
            driver.find_element(By.CLASS_NAME, 'market_commodity_buy_button').click()
        driver.find_element(By.ID, "market_buy_commodity_input_price").click()
        keyboard.send("Ctrl+A, Delete")
        keyboard.write(str(price))
        driver.find_element(By.ID, "market_buy_commodity_input_quantity").click()
        keyboard.send("Ctrl+A, Delete")
        keyboard.write(str(quantity))
        driver.find_element(By.ID, "market_buyorder_dialog_accept_ssa_label").click()
        driver.find_element(By.ID, "market_buyorder_dialog_purchase").click()
        successful_items.append(driver.current_url)
        return True
    except NoSuchElementException:
        return False
    except Exception as e:
        print(e)


def goto_page(driver, item):
    if type(item.link) == list:
        for link in item.link:
            if link in successful_items:
                continue
            driver.get(link)
            place_order(driver, item.type, item.price, item.quantity)
    elif type(item.link) == str:
        if item.link in successful_items:
            return True
        driver.get(item.link)
        place_order(driver, item.type, item.price, item.quantity)
        return True


def save_old_collections():
    profile_id = profile_ids[0]
    driver = change_profile(profile_id)
    collection_names = get_all_collections(driver)
    with open("old_collections.txt", "w") as file:
        json.dump(collection_names, file)


def get_old_collections():
    with open("old_collections.txt", "r") as file:
        return json.load(file)


def get_all_collections(driver):
    if driver.current_url != "https://steamcommunity.com/market/search?appid=730":
        driver.get("https://steamcommunity.com/market/search?appid=730")
    else:
        driver.refresh()
    driver.find_element(By.CLASS_NAME, "market_search_advanced_button").click()
    driver.implicitly_wait(0.01)
    page = driver.page_source

    # getting collection from combobox
    try:
        sticker_collection = [option.get("value") for option in BeautifulSoup(page, "lxml").find("select", attrs={"name": "category_730_StickerCapsule[]"}).children if option]
        agent_skins_options = [option.get("value") for option in BeautifulSoup(page, "lxml").find("select", attrs={"name": "category_730_ItemSet[]"}).children if option]
    except Exception as e:
        print(e)
        agent_skins_options = []
        sticker_collection = []

    all_labels = [option.get("for") for option in
                  BeautifulSoup(page, "lxml").find_all("label", attrs={"class": "econ_tag_filter_label"})]

    patch_collections = ['tag' + label[20:] for label in all_labels if label[:20] == 'tag_730_PatchCapsule']
    graffiti_collections = ['tag' + label[20:] for label in all_labels if label[:20] == 'tag_730_SprayCapsule']
    agent_collections = [option for option in agent_skins_options if option.find("characters") != -1]
    skin_collections = [option for option in agent_skins_options if option.find("characters") == -1]

    collection_names = {"Agents": agent_collections, "skin": skin_collections, "Patches": patch_collections,
                        "Stickers": sticker_collection, "graffiti": graffiti_collections}
    return collection_names


def identify_new_collections(driver):
    collection_names = get_all_collections(driver)
    old_collection_names = get_old_collections()
    res = {"Agents": [], "skin": [], "Patches": [], "Stickers": [], "graffiti": []}
    for item_type in collection_names.keys():
        res[item_type].extend(list(set(collection_names[item_type]) - set(old_collection_names[item_type])))
    return res


def generate_filter_url(item_class, item_collection, item_rarity=None, **kwargs):
    if item_rarity is None:
        item_rarity = "any"
    url = "https://steamcommunity.com/market/search?appid=730"
    url += f"&category_730_Rarity%5B%5D={item_rarity}"
    if item_class == "Stickers":
        url += f"&category_730_StickerCapsule%5B%5D={item_collection}"
    elif item_class == "Patches":
        url += f"&category_730_PatchCapsule%5B%5D={item_collection}"
    elif item_class == "Agents":
        url += f"&category_730_ItemSet%5B%5D={item_collection}"
    elif item_class == "skin":
        url += f"&category_730_ItemSet%5B%5D={item_collection}"
        url += f"&category_730_Exterior%5B%5D={kwargs['wear']}"
        if kwargs['stat_track']:
            url += "&category_730_Quality%5B%5D=tag_strange"
        else:
            url += "&category_730_Quality%5B%5D=tag_normal"
    return url

async def get_links_by_filter(session, url):
    global proxy_no
    async with session.get(url['link'], proxy=proxies[proxy_no]) as response:

        if response.status == 200:
            links = [link.get("href")
                     for link in BeautifulSoup(await response.text(), "lxml")
                     .find_all("a", class_="market_listing_row_link")]
            print(f"Got {len(links)} links from {url['link']}")
            return {"links": links, "rarity": url['rarity'], "item_type": url['item_type']}

        elif response.status == 429:
            print(f"Proxy is done. Changing...")
            proxy_no = (proxy_no + 1) % len(proxies)
            return await get_links_by_filter(session, url)

        else:
            print(f"Error: {response.status}")
            return []

def get_links_noproxy(driver, url):
    driver.get(url['link'])
    page = driver.page_source
    links = [link.get("href")
             for link in BeautifulSoup(page, "lxml")
             .find_all("a", class_="market_listing_row_link")]
    print(f"Got {len(links)} links from {url['link']}")
    return {"links": links, "rarity": url['rarity'], "item_type": url['item_type']}

async def parse_all_filters(urls):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for url in urls:
            tasks.append(asyncio.ensure_future(get_links_by_filter(session, url)))
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results

def parse_all_filters_noproxy(driver, urls):
    results = []
    for url in urls:
        results.append(get_links_noproxy(driver, url))
    return results


def change_profile(profile_id, prev_driver=None):
    if prev_driver:
        prev_driver.close()
    req_url = f"http://localhost:3001/v1.0/browser_profiles/{profile_id}/start?automation=1"
    try:
        response_json = requests.get(req_url).json()
        port = response_json['automation']['port']
    except KeyError:
        requests.get(f"http://localhost:3001/v1.0/browser_profiles/{profile_id}/stop")
        time.sleep(1)
        response_json = requests.get(req_url).json()
        port = response_json['automation']['port']

    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{port}")
    return webdriver.Chrome(driver_path, chrome_options=chrome_options)


proxy_no = 0
account_no = 0
driver_path = user_data.get_data()["driver_path"]
profile_ids = user_data.get_data()["accounts"]
proxies = user_data.get_data()["proxy"]

successful_items = []

def main():
    account_id = profile_ids[account_no]
    driver = change_profile(account_id)

    while not keyboard.is_pressed('F4'):
        new_collections = identify_new_collections(driver)
        if list(new_collections.values()) == [[], [], [], [], []]:
            print("No new collections")
            time.sleep(5)
        else:
            print(new_collections)
            items = []
            for item_type in new_collections.keys():
                for item_collection in new_collections[item_type]:
                    if item_type == "skin":
                        collection = SkinCollection(item_collection)
                    else:
                        collection = Collection(item_type, item_collection)
                    items.extend(collection.get_all_items())

            if not items:
                print("No new items, waiting 10s...")
            else:
                print(f"Found {len(items)} new items")

            for item in items:
                goto_page(driver=driver, item=item)

            time.sleep(310 / len(proxies))
    driver.close()


if __name__ == '__main__':
    #main()

    account_id = profile_ids[0]
    driver = change_profile(account_id)

    url1 = generate_filter_url("Agents", "tag_set_op11_characters", "tag_Rarity_Mythical_Character")
    url2 = generate_filter_url("Agents", "tag_set_op11_characters", "tag_Rarity_Legendary_Character")

    links = parse_all_filters_noproxy(driver, [{"link": url1, "rarity": "tag_Rarity_Mythical_Character", "item_type": "Agents"}, {"link": url2, "rarity": "tag_Rarity_Legendary_Character", "item_type": "Agents"}])
    print(links)