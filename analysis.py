from item_class import *

def decode_link(link: str, collection: str, item_class: str, item_rarity: str, **kwargs):
    temp = link.replace("https://steamcommunity.com/market/listings/730/", "").replace("%20", "").replace("%28",
                                                                                                          "(").replace(
        "%29", ")").replace("%7C", "|")
    temp = temp.split("|")
    if item_class == "Sticker":
        return Item(type_="Sticker", name=temp[1], link=link, collection=collection, rarity=item_rarity)
    elif item_class == "Patch":
        return Item(type_="Patch", name=temp[1], link=link, collection=collection, rarity=item_rarity)
    elif item_class == "Agent":
        return Item(type_="Agent", name=temp[1], link=link, collection=collection, rarity=item_rarity)
    elif item_class == "Skin":
        return Item(type_="Skin", name=temp[1], link=link, collection=collection, rarity=item_rarity,
                    wear=kwargs["wear"], stat_trak=kwargs["stat_track"])


def analyze_links(all_data, links):
    for link in links:
        pass
