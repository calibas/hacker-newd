from http.server import HTTPServer
import hnserver, json, sched, time
import threading, urllib.request, webbrowser

url_base = 'https://hacker-news.firebaseio.com/v0'
item_base = url_base + '/item/'

top_stories = url_base + '/topstories'
best_stories = url_base + '/beststories'
new_stories = url_base + '/newstories'

# How many stories to display, max 500 (max 200 for best_stories)
length = 100

# How much should the algorithm favor recent stories.
# Recommended values between 1.0 (none) and 2.0 (heavily favor recent)
favor_recent = 1.2

# Port for HTTP server on localhost
server_port = 3001

item_list = []

def main():
    global item_list

    # Separate thread that pulls data from Firebase
    # and saves to item_list
    u_thread = threading.Thread(target=update_thread)
    u_thread.setDaemon(True)
    u_thread.start()

    # Sleep until item_list is full
    while len(item_list) < length:
        time.sleep(1)

    # So we can pass item_list when using HTTPServer
    def handler(*args):
        hnserver.HNServer(item_list, *args)

    web_server = HTTPServer(("localhost", server_port), handler)
    server_url = f"http://localhost:{server_port}"
    print(f"Server started {server_url}")
    
    # Open in default web browser 
    webbrowser.open(server_url)
    
    try:
        web_server.serve_forever()
    except KeyboardInterrupt:
        pass

    web_server.server_close()
    print("Server stopped.")

def update_thread():
    update_list()
    s = sched.scheduler(time.time, time.sleep)
    def repeat_update_list(sc): 
        update_list()
        sc.enter(300, 1, repeat_update_list, (sc,))
    s.enter(300, 1, repeat_update_list, (s,))
    s.run()

def update_list():
    global item_list

    print('Fetching data from API, just a moment...')
    
    top = fetch_list(f'{top_stories}.json')
    item_list = []
    for index, item_id in enumerate(top[0:length]):
        item = fetch_item(item_id)
        if item:
            item['age'] = (time.time() - item['time'])/60
            item['heat'] = round(item['score']/pow(item['age'], favor_recent), 5)
            item['pos'] = index + 1
            item_list.append(item)
        else:
            print(f"Error fetching item_id {item_id}")

    item_list = sorted(item_list, key=lambda d: d['heat'], reverse=True)
    # print('')
    # for index, item in enumerate(item_list):
    #     print(
    #         f"{index + 1} ({item['pos']}): ({item['heat']}) - {item['title']} [{item['url']}] {item['id']}")
    print('')
    print('Downranked:')
    for index, item in enumerate(item_list):
        if item['age'] < 120 and item['pos'] - index > 10:
            print(
                f"{index + 1} ({item['pos']}): ({item['heat']}) - {item['title']} [{item['url']}] {item['id']}")
    print('')
    print('Upranked:')
    for index, item in enumerate(item_list):
        if item['age'] < 120 and  index - item['pos'] > 10:
            print(
                f"{index + 1} ({item['pos']}): ({item['heat']}) - {item['title']} [{item['url']}] {item['id']}")
    print('')

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
