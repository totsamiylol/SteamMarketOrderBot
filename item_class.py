""" Steam Community Market Item Class """


class Item:
    """ Item Class """
    def __init__(self, type_, rarity, price=0, quantity=0, collection=None, link=None):
        self.type = type_
        self.link = link
        self.price = price
        self.quantity = quantity
        self.collection = collection
        self.rarity = rarity

    def __str__(self):
        return f"Type: {self.type}\nRarity: {self.rarity}\nPrice: {self.price}\nQuantity: {self.quantity}\nLink: {self.link}\n\n"

    def __repr__(self):
        return f"Type: {self.type}\nRarity: {self.rarity}\nPrice: {self.price}\nQuantity: {self.quantity}\nLink: {self.link}\n\n"

    def __eq__(self, other):
        return self.link == other.link

    def __hash__(self):
        return hash(self.link)


class SkinItem(Item):
    """ Skin Item Class """
    def __init__(self, type_, is_operation, rarity, price=0, quantity=0, collection=None, link=None, wear=None, stat_trak=False):
        super().__init__(type_, rarity, price, quantity, collection, link)
        self.wear = wear
        self.stat_trak = stat_trak
        self.is_operation = is_operation

    def __repr__(self):
        return f"Type: {self.type}\nRarity: {self.rarity}\nWear: {self.wear}\nStatTrak: {self.stat_trak}\nPrice: {self.price}\nQuantity: {self.quantity}\nLink: {self.link}\n\n"

    def __str__(self):
        return f"Type: {self.type}\nRarity: {self.rarity}\nWear: {self.wear}\nStatTrak: {self.stat_trak}\nPrice: {self.price}\nQuantity: {self.quantity}\nLink: {self.link}\n\n"




