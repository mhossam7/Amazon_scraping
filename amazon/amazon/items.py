# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html



from scrapy import Item, Field



class AmazonItem(Item):



    url = Field()
    name = Field()
    price = Field()
    stars = Field()
    Rating = Field()
    feature_bullets = Field()
    images = Field()
    variant_data = Field()
    Payment = Field()
