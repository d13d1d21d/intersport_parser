import json
import pandas as pd
import html

from utils import *
from proxy_client import *
from bs4 import BeautifulSoup as bs
from dataclasses import dataclass


logger = init_logger(
    f"logs/{dt.now().strftime("%Y-%m-%d")}.log", 
    "%(asctime)s %(levelname)s %(message)s",
    logging.ERROR
)

@dataclass
class ProductData:
    url: str
    spu: str
    sku: str
    description: str
    category: str
    color: str
    size: str
    name: str
    brand: str
    price: float
    in_stock: int
    images: str

class Parser:
    BASE = "https://www.intersport.de"

    def __init__(
        self, 
        proxy_client: ProxyClient, 
        url_path: str, 
        category: str
    ) -> None:
        self.proxy_client = proxy_client
        self.url_path = url_path
        self.category = category

    def get_n_pages(self) -> int:
        return int(bs(
            self.proxy_client.http("GET", self.BASE + self.url_path + "?filterprice=15.00-300.00").text,
            "html.parser"
        ).find("div", { "data-pages": True }).get("data-pages"))

    def get_urls(self, page: int) -> list[str]:
        try:
            url = self.BASE + self.url_path + f"?filterprice=15.00-300.00&p={page}"
            product_list = bs(
                self.proxy_client.http("GET", url).text, 
                "html.parser"
            ).find("div", { "data-articlecount": True })

            return list(
                x.get("href")
                for x in product_list.find_all("a")
            )
        except:
            logger.error(f"Ошибка в извлечении ссылок на странице {page}. URL: {url}", exc_info=True)
    
    def parse_url(self, url: str) -> ProductData:
        try:
            page_html = bs(self.proxy_client.http("GET", url).text, "html.parser")
            products = []
            
            if variants := page_html.select("script[class*='article-variant']"):
                variants = json.loads(variants[0].text).get("variants")
                tracking_data = page_html.find("input", { "type": "hidden", "data-brand": True })
                
                description = html.unescape(page_html.select('div[class*="description"]')[0].select('div[class*="description"]')[0].text.replace("\n", "").strip())
                spu = url.split("/")[4]
                name = html.unescape(tracking_data.get("data-title"))
                brand = tracking_data.get("data-brand")

                for i in variants:
                    products.append(
                        ProductData(
                            url,
                            spu,
                            i.get("ordernumber"),
                            description,
                            self.category,
                            i.get("colorName").lower(),
                            i.get("sizeName"),
                            name,
                            brand,
                            float(i.get("price")),
                            int(i.get("inStock")),
                            i.get("images") + "&effects=Pad(cc,ffffff),Matte(FFFFFF)&width=1400&height=1400"
                        )
                    )

            return products
        
        except:
            logger.error(f"Ошибка в парсинге товара. URL: {url}", exc_info=True)


PREFIX = "ITR-"
def create_df(products: list[ProductData], stocks: bool = False) -> pd.DataFrame:
    if stocks:
        data = {
            "url": [],
            "brand": [],
            "shop_sku": [],
            "newmen_sku": [],
            "in_stock": [],
            "price": []
        }
    else:
        data = {
            "url": [],
            "artikul": [],
            "shop_sku": [],
            "newmen_sku": [],
            "bundle_id": [],
            "product_name": [],
            "producer_size": [],
            "price": [],
            "price_before_discount": [],
            "base_type": [],
            "commercial_type": [],
            "brand": [],
            "origin_color": [],
            "color_rgb": [],
            "color": [],
            "manufacturer": [],
            "main_photo": [],
            "additional_photos": [],
            "number": [],
            "vat": [],
            "ozon_id": [],
            "gtin": [],
            "weight_in_pack": [],
            "pack_width": [],
            "pack_length": [],
            "pack_height": [],
            "images_360": [],
            "note": [],
            "keywords": [],
            "in_stock": [],
            "card_num": [],
            "error": [],
            "warning": [],
            "num_packs": [],
            "origin_name": [],
            "category": [],
            "content_unit": [],
            "net_quantity_content": [],
            "instruction": [],
            "info_sheet": [],
            "product_description": [],
            "non_food_ingredients_description": [],
            "application_description": [],
            "company_address_description": [],
            "care_label_description": [],
            "country_of_origin_description": [],
            "warning_label_description": [],
            "sustainability_description": [],
            "required_fields_description": [],
            "additional_information_description": [],
            "hazard_warnings_description": [],
            "leaflet_description": []
        }

    for i in products:
        if stocks:
            data["url"].append(i.url)
            data["brand"].append(i.brand)
            data["shop_sku"].append(i.sku)
            data["newmen_sku"].append(PREFIX + i.sku)
            data["in_stock"].append(i.in_stock)
            data["price"].append(i.price)
        else:
            if not i.images: i.images = ["", ""]

            data["url"].append(i.url)
            data["artikul"].append(i.sku)
            data["shop_sku"].append(i.sku)
            data["newmen_sku"].append(PREFIX + i.sku)
            data["bundle_id"].append(i.spu)
            data["product_name"].append(i.name)
            data["producer_size"].append(i.size)
            data["price"].append(i.price)
            data["price_before_discount"].append("")
            data["base_type"].append("")
            data["commercial_type"].append("")
            data["brand"].append(i.brand)
            data["origin_color"].append(i.color)
            data["color_rgb"].append("")
            data["color"].append(i.color)
            data["manufacturer"].append("")
            data["main_photo"].append(i.images[0])
            data["additional_photos"].append(",".join(i.images[1:]))
            data["number"].append("")
            data["vat"].append("")
            data["ozon_id"].append("")
            data["gtin"].append("")
            data["weight_in_pack"].append("")
            data["pack_width"].append("")
            data["pack_length"].append("")
            data["pack_height"].append("")
            data["images_360"].append("")
            data["note"].append("")
            data["keywords"].append("")
            data["in_stock"].append(i.in_stock)
            data["card_num"].append("")
            data["error"].append("")
            data["warning"].append("")
            data["num_packs"].append("")
            data["origin_name"].append(i.name)
            data["category"].append(i.category)
            data["content_unit"].append("")
            data["net_quantity_content"].append("")
            data["instruction"].append("")
            data["info_sheet"].append("")
            data["product_description"].append(i.description)
            data["non_food_ingredients_description"].append("")
            data["application_description"].append("")
            data["company_address_description"].append("")
            data["care_label_description"].append("")
            data["country_of_origin_description"].append("")
            data["warning_label_description"].append("")
            data["sustainability_description"].append("")
            data["required_fields_description"].append("")
            data["additional_information_description"].append("")
            data["hazard_warnings_description"].append("")
            data["leaflet_description"].append("")

    return pd.DataFrame(data)
