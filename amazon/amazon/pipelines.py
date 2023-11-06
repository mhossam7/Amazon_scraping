# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy import item
import json


class AmazonPipeline:
    def process_item(self, item, spider):


        adapter = ItemAdapter(item)

        Rating_string = adapter.get("Rating")

        if Rating_string != "":
            Split_Rating_array = Rating_string.split(" ")
            adapter["Rating"] = int(Split_Rating_array[0])

        star_string = str(adapter.get("stars"))
        if star_string is None:
            adapter["stars"] = ""
        else:

            Split_Star_array = star_string.split(" ")

            adapter["stars"] = float(Split_Star_array[0])

        Keywords = ["variant_data","images",'feature_bullets']
        for keyword in Keywords:
            Join_Dic = adapter.get(keyword)
            adapter[keyword] = json.dumps(Join_Dic)


        value = adapter.get("price")
        value = value.replace("$", "")
        value = value.replace(",", "")
        adapter["price"] = float(value)



        return item


import mysql.connector


class SaveToMySQLPipeline:

    def __init__(self):
        self.conn = mysql.connector.connect(
            user = "root",
            password = "X12345@gmail",
            database = "Amazon",
        )

        self.cur = self.conn.cursor()
        self.cur.execute(
            """
            CREATE TABLE IF NOT EXISTS Amazon(
                id int NOT NULL  auto_increment,
                url VARCHAR(500),
                name VARCHAR(255),
                price DEC(65, 2) NOT NULL,
                stars DECIMAL,
                Rating INTEGER,
                feature_bullets TEXT,
                images TEXT,
                variant_data TEXT,
                PRIMARY KEY (id)
            )
            """)

    def process_item(self, item, spider):


        self.cur.execute(""" insert into Amazon(
            url,
            name,
            price,
            stars,
            Rating,
            feature_bullets,
            images,
            variant_data
            ) values (
                %s, 
                %s,
                %s,
                %s,
                %s,                    
                %s,
                %s,
                %s
                )""", (
            item["url"],
            item["name"],
            item["price"],
            item["stars"],
            item["Rating"],
            item["feature_bullets"],
            item["images"],
            item["variant_data"],

        ))



        self.conn.commit()

        return item

    def close_spider(self,spider):

        self.cur.close()
        self.conn.close()