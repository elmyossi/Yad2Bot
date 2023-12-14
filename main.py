import requests
import json
import time
from urllib.parse import urlencode
from telegram import Bot, InputMediaPhoto
from io import BytesIO
from datetime import datetime
async def send_message_async(bot, chat_id, message_text):
    await bot.send_message(chat_id=chat_id, text=message_text, parse_mode='Markdown')
    print("Message sent successfully!")


def convert_str_to_date(date_as_str):
    if not date_as_str:
        return date_as_str
    return datetime.strptime(date_as_str, "%Y-%m-%d %H:%M:%S")


async def main(params, brand):
    bot_token = '6410021064:AAHuHO1Q4EVcIhLD8nzWIv_qVINyuvgtouk'
    bot = Bot(token=bot_token)

    # Replace 'YOUR_CHAT_ID' with the actual chat ID
    chat_id_yossi = 1307355686
    chat_id_amit = 6868083262

    TotalCheck = False
    json_file_path = f'{brand}.json'
    try:
        with open(json_file_path, 'r') as json_file:
            unique_date_added = json.load(json_file)
    except FileNotFoundError:
        unique_date_added = []

    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Cookie': '__ssds=3; __ssuzjsr3=a9be0cd8e; __uzmaj3=2482bab2-e643-4981-b19f-ca5d3afc7132; __uzmbj3=1687852959; __uzmlj3=PyqZE7dcY4wB1d0cwdis7E=; y2018-2-cohort=87; leadSaleRentFree=82; __uzmb=1687852961; __uzma=1489c434-41b7-4cb2-ba68-54014c40ede2; __uzme=7900; guest_token=eyJhbGciOiJIUz3ZS04ZWQ0LTQ4NDItOTE3YS0zjoxNjg3ODUyOTYxLCJleHAiOjE3MjEwNzY4MTQ4MDN9.15-hRYa5G_B7ASy6lrVllacDfAG8zz08c_riM57i1vs; abTestKey=79; use_elastic_search=1; canary=never; __uzmcj3=105419468535; __uzmdj3=1690528114; __uzmfj3=7; server_env=production; y2_cohort_2020=8; favorites_userid=edd1063272547; __uzmd=; __uzmc=763',
        'Origin': 'https://www.yad2.co.il',
        'Pragma': 'no-cache',
        'Referer': 'https://www.yad2.co.il/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
        'mainsite_version_commit': '7c9a9c5c1fe45ec28c16bc473d25aad7141f53bd',
        'mobile-app': 'false',
        'sec-ch-ua': 'Not/A)Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': 'Windows',
    }
    # How many new apartment
    count = 0
    max_current_date_str = unique_date_added[0]
    max_current_date = convert_str_to_date(max_current_date_str)

    base_url = "https://gw.yad2.co.il/feed-search-legacy/vehicles/cars"
    params['page'] = 0
    # Encode the parameters
    encoded_params = urlencode(params)
    # Construct the final URL
    final_url = f"{base_url}?{encoded_params}"

    time.sleep(1)
    response = requests.get(final_url, headers=headers)
    if response.status_code != 200:
        print(f"Request failed with status code: {response.status_code}")

    data = response.json()
    # Process the JSON data as needed
    for d in data['data']['feed']['feed_items']:
        date_added_str = d.get('date_added')
        date_added = convert_str_to_date(date_added_str)
        try:
            if date_added and date_added > max_current_date:
                unique_date_added.append(date_added)
                if d['feed_source'] == "private":
                    count = count + 1
                    TotalCheck = True
                    area = d['AreaID_text']
                    price = d['price']
                    km = d['kilometers']
                    year = d['year']
                    hand = d['Hand_text']
                    prev_hand_k, prev_hand_v = d.get('more_details', {})[-2]['key'], d.get('more_details', {})[-2][
                        'value']
                    cur_hand_k, cur_hand_v = d.get('more_details', {})[-3]['key'], d.get('more_details', {})[-3][
                        'value']
                    Addid = "https://www.yad2.co.il/item/" + d['id']
                    if hand == 'יד שניה' and prev_hand_v != 'פרטית':
                        continue
                    await send_message_async(bot, chat_id_yossi,
                                             f' *איזור*: {area}, *מחיר*: {price}, *ק״מ*: {km} , *שנה*: {year}. *יד*:  {hand}, *{prev_hand_k}* {prev_hand_v}, *{cur_hand_k}* {cur_hand_v}. [קישור למודעה]({Addid}) ')

                    await send_message_async(bot, chat_id_amit,
                                             f' *איזור*: {area}, *מחיר*: {price}, *ק״מ*: {km} , *שנה*: {year}. *יד*:  {hand}, *{prev_hand_k}* {prev_hand_v}, *{cur_hand_k}* {cur_hand_v}. [קישור למודעה]({Addid}) ')

                    media_items = []
                    check = False
                    for image in d['images']:
                        image_url = d['images'][image]['src']
                        responseImage = requests.get(image_url)
                        image_bytes = BytesIO(responseImage.content)
                        # await bot.send_photo(chat_id=chat_id_yossi, photo=image_bytes)
                        media_items.append(InputMediaPhoto(media=image_bytes))
                        check = True

                    if check == True:
                        await bot.send_media_group(chat_id=chat_id_yossi, media=media_items)
                        await bot.send_media_group(chat_id=chat_id_amit, media=media_items)

        except (KeyError, ValueError):
            pass

        # Save the updated unique_date_added to the JSON file
    with open(json_file_path, 'w') as json_file:
        dates = [convert_str_to_date(d) for d in unique_date_added]
        max_date = max(dates)
        json.dump([max_date], json_file, default=str)

    return TotalCheck


if __name__ == "__main__":
    import asyncio

    loop = asyncio.get_event_loop()

    # Define the parameters
    # Toyota Corola
    params_toyota = {
        'manufacturer': 19,
        'model': 1428,
        'year': '2016-2023',
        'price': '0-71000',
        'priceOnly': 1,
        'km': '0-110000',
        'hand': '0-2',
        'ownerID': 1,
        'gearBox': 1,
    }

    # Hyundai i30, i25
    params_hyundai = {
        'manufacturer': 21,
        'model': '1726,1281',
        'year': '2016-2023',
        'price': '0-71000',
        'priceOnly': 1,
        'km': '0-120000',
        'hand': '0-2',
        'engineval': '1500--1',
        'ownerID': 1,
        'gearBox': 1,
    }
    # Suzuki Crossover
    params_suzuki = {
        'manufacturer': 36,
        'model': 2406,
        'year': '2017-2023',
        'price': '0-71000',
        'priceOnly': 1,
        'km': '0-120000',
        'hand': '0-2',
        'ownerID': 1,
        'gearBox': 1,
    }
    params_kia = {
        'manufacturer': 48,
        'model': 1653,
        'year': '2016-2023',
        'price': '0-71000',
        'priceOnly': 1,
        'km': '0-120000',
        'hand': '0-2',
        'ownerID': 1,
        'gearBox': 1,
    }
    params_mazda = {
        'manufacturer': 27,
        'model': 1645,
        'year': '2016-2023',
        'price': '0-71000',
        'priceOnly': 1,
        'km': '0-120000',
        'hand': '0-2',
        'ownerID': 1,
        'gearBox': 1,
    }

    checkNew1 = loop.run_until_complete(main(params_toyota, "Toyota"))
    checkNew2 = loop.run_until_complete(main(params_hyundai, "Hyundai"))
    checkNew3 = loop.run_until_complete(main(params_suzuki, "Suzuki"))
    checkNew4 = loop.run_until_complete(main(params_kia, "Kia"))
    checkNew5 = loop.run_until_complete(main(params_mazda, "Mazda"))

    # if checkNew1==False and checkNew2==False and checkNew3==False and checkNew1_amit==False and checkNew2_amit==False and checkNew3_amit==False:
    #     loop.run_until_complete(send_message_async(bot, chat_id_yossi, "*אין מכוניות חדשות*"))
    #     loop.run_until_complete(send_message_async(bot, chat_id_amit, "*אין מכוניות חדשות*"))
