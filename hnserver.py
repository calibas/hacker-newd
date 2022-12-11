from http.server import BaseHTTPRequestHandler

class HNServer(BaseHTTPRequestHandler):
    def __init__(self, item_list, mutex, *args):
        self.item_list = item_list
        self.mutex = mutex
        BaseHTTPRequestHandler.__init__(self, *args)

    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self.mutex.acquire()
            try:
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()

                header = """
                    <!DOCTYPE html>
                    <html><head>
                    <meta charset='utf-8'>
                    <title>Hacker Newd</title>
                    <link rel='stylesheet' type='text/css' href='style.css'>
                    </head>
                    """
                self.html_output(header)

                self.html_output("""
                    <body>
                    <ol>
                    """)
                for index, item in enumerate(self.item_list):
                    age = "0m"
                    if item['age'] >= 60:
                        age = f"{round(item['age']/60)}h"
                    else:
                        age = f"{round(item['age'])}m"
                    pos_color = get_pos_color(item['pos'], index + 1)
                    self.html_output(
                        f"""
                            <li class="item">
                                <div class="index">{index + 1}</div>
                                <div class="item-info">
                                    <div class="pos" style="background-color:{pos_color}">{item['pos']}</div>
                                    <div class="heat">{round(item['heat'], 4)}</div>
                                    <div class="age">{age}</div>
                                </div>
                                <div class="link"><a href='{item['url']}'>{item['title']}</a></div> 
                                <div class="comments">[<a href='{get_hn_url(item['id'])}'>comments</a>]</div>
                            </li>
                        """)
                self.html_output("""
                    </ol>
                    </body>
                    </html>
                    """)
            finally:
                self.mutex.release()

        elif self.path == "/style.css":
            with open("style.css", 'rb') as file:
                self.send_response(200)
                self.send_header("Content-type", "text/css")
                self.end_headers()

                self.wfile.write(file.read())

        else:
            self.send_response(404)
            self.end_headers()

    def html_output(self, html_txt):
        self.wfile.write(bytes(html_txt, "utf-8"))


def get_hn_url(item_id):
    return f"https://news.ycombinator.com/item?id={item_id}"

def get_pos_color(item_pos, index):
    pos_color = "#fff"
    if item_pos - index > 10:
        pos_color = "#ffe4e4"
    if item_pos - index > 20:
        pos_color = "#ffc3c3"
    if item_pos - index > 50:
        pos_color = "#ff9595"
    if index - item_pos > 10:
        pos_color = "#d9fdcf"
    if index - item_pos > 20:
        pos_color = "#9effa4"
    if index - item_pos > 30:
        pos_color = "#4fff5a"
    
    return pos_color
    