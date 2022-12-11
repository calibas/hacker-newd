from http.server import HTTPServer
import hnserver
import json
import sched
import time
import threading
import urllib.request
import webbrowser
import numpy as np

url_base = 'https://hacker-news.firebaseio.com/v0'
item_base = url_base + '/item/'

top_stories = url_base + '/topstories'
best_stories = url_base + '/beststories'
new_stories = url_base + '/newstories'

# Top, best or new stories
hn_stories = top_stories

# How many stories to display, max 500 (max 200 for best_stories)
length = 100

# How much should the algorithm penalize older stories.
# Recommended values between 1.0 (none) and 2.0 (heavily favor recent)
# HN appears to use a value around 1.5 (top) and 1.0 (best)
favor_recent = 1.5

# Order by heat, age, or default
order_by = "heat"

# Time limit for checking downranked/upranked stories
rank_time_limit = 180

# Port for HTTP server on localhost
server_port = 3001

item_list = []


def main():
    global item_list

    # Use a mutex to prevent separate threads from
    # accessing item_list at the same time
    mutex = threading.Lock()

    # Separate thread that pulls data from Firebase
    # and saves to item_list
    u_thread = threading.Thread(target=update_thread, args=[mutex])
    u_thread.setDaemon(True)
    u_thread.start()

    # Sleep until item_list is full
    list_len = 0
    while list_len < length:
        time.sleep(1)
        mutex.acquire()
        try:
            list_len = len(item_list)
        finally:
            mutex.release()

    # Use handler so we can pass item_list when using HTTPServer
    def handler(*args):
        hnserver.HNServer(item_list, mutex, *args)

    web_server = HTTPServer(("localhost", server_port), handler)
    server_url = f"http://localhost:{server_port}"
    print(f"Server started {server_url}")

    # Open in default web browser
    webbrowser.open(server_url)

    # Run web server until keyboard interrupt
    try:
        web_server.serve_forever()
    except KeyboardInterrupt:
        pass

    web_server.server_close()
    print("Server stopped.")


def update_thread(mutex):
    # Thread to run update_list() repeatedly using scheduler
    update_list(mutex)
    s = sched.scheduler(time.time, time.sleep)

    def repeat_update_list(sc):
        update_list(mutex)
        sc.enter(300, 1, repeat_update_list, (sc,))
    s.enter(300, 1, repeat_update_list, (s,))
    s.run()


def update_list(mutex):
    global item_list
    temp_list = []

    print('Fetching data from API, just a moment...')

    top = fetch_list(f'{hn_stories}.json')
    for index, item_id in enumerate(top[0:length]):
        item = fetch_item(item_id)
        if item:
            item['age'] = (time.time() - item['time'])/60
            
            # Subtract 1 from score when it's less than an hour old,
            # this is so heat wont be as high for very new stories
            # time_adj = 0
            # if item['age'] < 60:
            #     time_adj = 1
            # item['heat'] = round((item['score'] - time_adj) /
            #                      pow(item['age'], favor_recent), 5)
            
            # Halve score when it's less than an hour old,
            # this is so heat wont be as high for very new stories
            time_adj = 1.0
            # if item['age'] < 60:
            #     time_adj = 0.5
            # if item['age'] > 600:
            #     time_adj = 1.5
            item['heat'] = round((item['score'] * time_adj) /
                                  pow(item['age'], favor_recent), 5)
            
            item['pos'] = index + 1
            temp_list.append(item)
            print(f" {round((item['pos']/length) * 100)}% complete", end='\r'),
        else:
            print(f"Error fetching item_id {item_id}")
    print('')

    temp_list = sorted(temp_list, key=lambda d: d['heat'], reverse=True)
    # print('')
    # for index, item in enumerate(temp_list):
    #     print(
    #         f"{index + 1} ({item['pos']}): ({item['heat']}) - {item['title']} [{item['url']}] {item['id']}")
    print('')
    if hn_stories != new_stories:
        print('Downranked:')
        for index, item in enumerate(temp_list):
            if item['age'] < rank_time_limit and item['pos'] - index > 10:
                print(
                    f"{index + 1} ({item['pos']}): ({item['heat']}) - {item['title']} [{item['url']}] {item['id']}")
        print('')
        print('Upranked:')
        for index, item in enumerate(temp_list):
            if item['age'] < rank_time_limit and index - item['pos'] > 10:
                print(
                    f"{index + 1} ({item['pos']}): ({item['heat']}) - {item['title']} [{item['url']}] {item['id']}")
        print('')

    if order_by == "age":
        temp_list = sorted(temp_list, key=lambda d: d['age'])
    if order_by == "default":
        temp_list = sorted(temp_list, key=lambda d: d['pos'])

    x = np.arange(1, len(temp_list) + 1)
    y = np.array([])
    for item in temp_list:
        y = np.append(y, item['pos'])

    corr = np.corrcoef(x, y)
    print(f"r: {round(corr[0][1], 5)}")
    
    mutex.acquire()
    try:
        item_list = temp_list
    finally:
        mutex.release()


def fetch_list(url):
    json_res = []
    try:
        with urllib.request.urlopen(url) as response:
            json_res = json.loads(response.read())
    except urllib.error.URLError:
        print(f"Error connecting to {url}")

    return json_res


def fetch_item(item_id):
    json_res = []
    try:
        with urllib.request.urlopen(f'{item_base}{item_id}.json') as response:
            json_res = json.loads(response.read())
            if not 'url' in json_res:
                json_res['url'] = hnserver.get_hn_url(item_id)
    except urllib.error.URLError:
        print(f"Error connecting to {item_base}{item_id}.json")

    return json_res


if (__name__ == '__main__'):
    main()
