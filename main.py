from script import *
from proxy import *
from time import *

wear = ["tag_WearCategory0", "tag_WearCategory1", "tag_WearCategory2", "tag_WearCategory3", "tag_WearCategory4"]
collection = {
    'agent': "tag_set_op12_characters",
    'case': "tag_set_community_32",
    'collection': ["tag_set_op12_anubis", "tag_set_nuke_2022", "tag_set_overpass_2022", "tag_set_inferno_2022", "tag_set_anubis"],  # <------
    'patch': "tag_crate_patch_pack04"
}

rarity = {
    'agent': ["tag_Rarity_Rare_Character", "tag_Rarity_Mythical_Character", "tag_Rarity_Legendary_Character", "tag_Rarity_Ancient_Character"],
    'case': ["tag_Rarity_Rare_Weapon", "tag_Rarity_Mythical_Weapon", "tag_Rarity_Legendary_Weapon", "tag_Rarity_Ancient_Weapon"],
    'collection': ["tag_Rarity_Common_Weapon", "tag_Rarity_Uncommon_Weapon", "tag_Rarity_Rare_Weapon", "tag_Rarity_Mythical_Weapon"],
    'patch': ["tag_Rarity_Rare", "tag_Rarity_Mythical", "tag_Rarity_Legendary"],
    'sticker': ["tag_Rarity_Rare", "tag_Rarity_Mythical", "tag_Rarity_Legendary", "tag_Rarity_Ancient"]
}
my_proxies = [
"dimacherkas04:tpYgrmLHJx@88.216.34.42:50100",
"dimacherkas04:tpYgrmLHJx@193.31.60.34:50100",
"dimacherkas04:tpYgrmLHJx@193.31.60.186:50100",
"dimacherkas04:tpYgrmLHJx@193.31.60.180:50100",
"dimacherkas04:tpYgrmLHJx@89.117.250.105:50100",
"dimacherkas04:tpYgrmLHJx@89.117.250.80:50100",
"dimacherkas04:tpYgrmLHJx@193.31.60.184:50100",
"dimacherkas04:tpYgrmLHJx@193.31.60.200:50100",
"dimacherkas04:tpYgrmLHJx@193.31.60.218:50100",
"dimacherkas04:tpYgrmLHJx@193.31.60.109:50100"
]


link1 = generate_filter_url("skin", "tag_set_community_32", "tag_Rarity_Rare_Weapon", wear="tag_WearCategory0", st=True)
links = parse_item_links(link1)


#### PROXY NOT WORKING ####



