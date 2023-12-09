import requests
import json
import time
from urllib.parse import urlencode
from telegram import Bot, InputMediaPhoto
from io import BytesIO


async def send_message_async(bot, chat_id, message_text):
    await bot.send_message(chat_id=chat_id, text=message_text,parse_mode='Markdown')
    print("Message sent successfully!")


async def main(params, car_brand,bot, chat_id_yossi):
    TotalCheck=False
    json_file_path = 'unique_date_added.json'
    try:
        with open(json_file_path, 'r') as json_file:
            unique_date_added = set(json.load(json_file))
    except FileNotFoundError:
        unique_date_added = set()

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
    for i in range(1):
        base_url = "https://gw.yad2.co.il/feed-search-legacy/vehicles/cars"
        params['page'] = i
        # Encode the parameters
        encoded_params = urlencode(params)
        # Construct the final URL
        final_url = f"{base_url}?{encoded_params}"
        time.sleep(1)
        response = requests.get(final_url, headers=headers)


        if response.status_code == 200:
            data = response.json()
            # How many new cars
            for d in data['data']['feed']['feed_items']:
                try:
                    date_added = d.get('date_added')
                    if date_added not in unique_date_added:
                        if d.get('feed_source') == "private":
                            count = count + 1
                            TotalCheck = True
                except (KeyError, ValueError):
                    pass
    if count>0:
        await send_message_async(bot, chat_id_yossi, f'New cars of type *{car_brand}*: {count}')


    for i in range(1):
        base_url = "https://gw.yad2.co.il/feed-search-legacy/vehicles/cars"
        params['page'] = i
        # Encode the parameters
        encoded_params = urlencode(params)
        # Construct the final URL
        final_url = f"{base_url}?{encoded_params}"

        time.sleep(1)
        response = requests.get(final_url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            # Process the JSON data as needed
            for d in data['data']['feed']['feed_items']:
                try:
                    if d['feed_source']=="private": # דירות לא מתיווך
                        area = d['AreaID_text']
                        price=d['price']
                        km=d['kilometers']
                        year=d['year']
                        hand= d['Hand_text']
                        prev_hand_k, prev_hand_v= d.get('more_details',{})[-2]['key'], d.get('more_details',{})[-2]['value']
                        cur_hand_k, cur_hand_v = d.get('more_details', {})[-3]['key'], d.get('more_details', {})[-3]['value']
                        date_added = d['date_added']
                        Addid="https://www.yad2.co.il/item/"+d['id']
                        if date_added not in unique_date_added:
                            unique_date_added.add(date_added)
                            if hand == 'יד שניה' and prev_hand_v != 'פרטית':
                                continue
                            await send_message_async(bot, chat_id_yossi,f' *איזור*: {area}, *מחיר*: {price}, *ק״מ*: {km} , *שנה*: {year}. *יד*:  {hand}, *{prev_hand_k}* {prev_hand_v}, *{cur_hand_k}* {cur_hand_v}. [קישור למודעה]({Addid}) ')

                            media_items = []
                            check = False
                            for image in d['images']:
                                image_url=d['images'][image]['src']
                                responseImage = requests.get(image_url)
                                image_bytes = BytesIO(responseImage.content)
                                #await bot.send_photo(chat_id=chat_id, photo=image_bytes)
                                media_items.append(InputMediaPhoto(media=image_bytes))
                                check=True

                            if check==True:
                                await bot.send_media_group(chat_id=chat_id_yossi, media=media_items)
                except (KeyError,ValueError):
                    pass
        else:
            print(f"Request failed with status code: {response.status_code}")

        # Save the updated unique_date_added to the JSON file
        with open(json_file_path, 'w') as json_file:
            json.dump(list(unique_date_added), json_file)

    return TotalCheck
if __name__ == "__main__":
    import asyncio
    loop = asyncio.get_event_loop()

    bot_token = '6410021064:AAHuHO1Q4EVcIhLD8nzWIv_qVINyuvgtouk'
    bot = Bot(token=bot_token)

    # Replace 'YOUR_CHAT_ID' with the actual chat ID
    chat_id_yossi = 1307355686

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

    checkNew1=loop.run_until_complete(main(params_toyota,"Toyota" ,bot,chat_id_yossi))
    checkNew2=loop.run_until_complete(main(params_hyundai, "Hyundai",bot,chat_id_yossi))
    checkNew3=loop.run_until_complete(main(params_suzuki, "Suzuki",bot,chat_id_yossi))

    if checkNew1==False and checkNew2==False and checkNew3==False:
        loop.run_until_complete(send_message_async(bot, chat_id_yossi, "*אין דירות חדשות*"))


