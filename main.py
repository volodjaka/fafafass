import time
import requests
from bs4 import BeautifulSoup
import telebot
import sys, os

bot = telebot.TeleBot("6133344065:AAFIsbw3STIFPqZ21FglFgX6xq2tl9LCEi8")

def scraper(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    items = soup.find_all("a", class_="am")
    print(soup)
    price = soup.find_all(string=lambda text: "€" in text)
    area = soup.find_all(string=lambda text: "м²" in text)
    area_farm = soup.find_all(string=lambda text: "га." in text)
    combined = []
    for i, item in enumerate(items):
        item_description = item.text
        area_farm = area_farm[0]
        if i + 1 >= len(price):
            item_price = None
        else:
            item_price = price[i + 1]
        try:
            item_price_m2 = price[i]
        except IndexError:
            item_price_m2 = None
        try:
            ad_area = area[0]
        except IndexError:
            ad_area = None
        combined.append({"description": item_description, "price": item_price, "pricem2": item_price_m2, "area": ad_area, "area_farm": area_farm})
    latest_items = combined
    data = []
    for item in latest_items[:1]:
        if item["area"] is None:
            area = item["area_farm"]
        else:
            area = item["area"]
        description = item["description"]
        price = item["price"]
        price_m2 = item["pricem2"]

        area_farm = item["area_farm"]
        data.append({"description": description, "price": price, "pricem2": price_m2, "area": area, "area_farm": area_farm})
    return data

@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(chat_id=message.chat.id, text="Starting data scraper...")
    urls = [
        "https://www.ss.com/ru/real-estate/plots-and-lands/daugavpils-and-reg/",
        "https://www.ss.com/ru/real-estate/homes-summer-residences/daugavpils-and-reg/visku-pag/",
        "https://www.ss.com/ru/real-estate/homes-summer-residences/daugavpils-and-reg/malinovas-pag/",
        "https://www.ss.com/ru/real-estate/farms-estates/daugavpils-and-reg/naujenes-pag/",
        "https://www.ss.com/ru/real-estate/farms-estates/daugavpils-and-reg/malinovas-pag/",
        "https://www.ss.com/ru/real-estate/farms-estates/daugavpils-and-reg/visku-pag/"
    ]
    sent_data = []
    first_cycle = 0
    while True:
        try:
            time.sleep(30)
            for url in urls:

                print(url)
                region = url.split("/")[-2]
                try:
                    data = scraper(url)
                except IndexError as e:
                    print(f"An error occurred: {e}")

                print(data)
                for item in data:
                    if item not in sent_data:
                        sent_data.append(item)
                        print(item)
                        if first_cycle == 0:
                            item_message ="Место: " + region+"\n" + "Тескт обьявления: " + f"{item['description']}\n" + "Цена общая: " + f"{item['price']}\n" + "Цена за квадрат: " + f"{item['pricem2']}\n" + "Общая площадь: " + f"{item['area']}\n"
                            bot.send_message(chat_id=message.chat.id, text=item_message)
                        else:
                            item_message = "Место: " + region + "\n" + "Тескт обьявления: " + f"{item['description']}\n" + "Цена общая: " + f"{item['price']}\n" + "Общая площадь: " + f"{item['area']}\n"
                            bot.send_message(chat_id=message.chat.id, text=item_message)
                        first_cycle = 1

        except Exception as e:
            bot.send_message(chat_id=message.chat.id, text=f"An error occurred: {e}")
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)

bot.polling()