import urllib3, json, logging, time

COOLQ_ENDPOINT = "http://localhost:5700/{}"
XKCD_ENDPOINT = "https://xkcd.com/{}/info.0.json"

POOLING_INTERVAL = 60*60


def get_http(url):
    print("GET {}".format(url))
    http = urllib3.PoolManager()
    response = http.request("GET", url)
    return response


def read_start():
    with open("start.txt", "r") as f:
        return int(f.read().strip())

def save_start(start):
    print("Saving new start {} to start.txt".format(start))
    with open("start.txt", "w") as f:
        f.write(str(start))

def get_xkcd_data(num):
    url = XKCD_ENDPOINT.format(num)
    response = get_http(url)
    if response.status != 200:
        print("Failed to fetch data from {}".format(url))
        return None
    print("Fetched data from {}".format(url))
    return json.loads(response.data.decode("utf-8"))

def get_friend_list():
    response = get_http(COOLQ_ENDPOINT.format('get_friend_list'))
    if response.status != 200:
        print("Failed to fetch friend list")
        return None
    return json.loads(response.data.decode("utf-8"))


def do_send(user_id, image):
    response = get_http(COOLQ_ENDPOINT.format(
        "send_private_msg?user_id={},message={}[CQ:image,file={}]".format(
            user_id, image, image
            )
    ))
    if response.status != 200:
        print("Failed to send image to {}".format(user_id))
        return
    print("Sent image to {}".format(user_id))

def action():
    curr = read_start()
    comic_data = get_xkcd_data(curr)
    if comic_data is None:
        return
    print("Sending data to CoolQ")
    for friend in get_friend_list()["data"]:
        do_send(friend["user_id"], comic_data["img"])
    save_start(curr + 1)
    

if __name__ == "__main__":
    print("Starting...")
    print("Using COOLQ_ENDPOINT: {}".format(COOLQ_ENDPOINT))
    print("Using XKCD_ENDPOINT: {}".format(XKCD_ENDPOINT))
    while True:
        try:
            action()
        except Exception as e:
            print("Exception: {}".format(e))
        time.sleep(POOLING_INTERVAL)
        
