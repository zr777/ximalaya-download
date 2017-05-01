import requests
from bs4 import BeautifulSoup
from threading import Thread, Lock
import os
import sys

os.chdir(r'E:\python\2017_4_20')

shared_dict = {}
# https://docs.python.org/3.6/faq/library.html#what-kinds-of-global-value-mutation-are-thread-safe
# http://stackoverflow.com/questions/6953351/thread-safety-in-pythons-dictionary
# d = {1:1}; import dis; dis.dis('d[1] = "x"')
# http://document.ihg.uni-duisburg.de/Documentation/Python/lib/node56.html
lock = Lock()

mp3_url = 'http://www.ximalaya.com/2452186/album/4015467'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/57.0.2987.133'
}

res = requests.get(mp3_url, headers=headers)
soup = BeautifulSoup(res.content, 'lxml')
mp3_ids = soup.select_one('.personal_body').attrs['sound_ids']
json_url = 'http://www.ximalaya.com/tracks/{id}.json'
mp3s = [json_url.format(id=i) for i in mp3_ids.split(',')]
n_workers = len(mp3s)


def get_mp3_from_json_url(json_url):
    mp3_info = requests.get(json_url, headers=headers).json()
    title = mp3_info['album_title'] + '+ ' + mp3_info['title'] + '.m4a'
    path = mp3_info['play_path']

    if os.path.exists(title):
        return 'Already exists'

    # http://stackoverflow.com/questions/13137817/how-to-download-image-using-requests
    try:
        with open(title, 'wb') as f:
            response = requests.get(path, stream=True)

            if not response.ok:
                # shared_dict.pop(title)
                print('error with', title)

            total_length = int(response.headers.get('content-length'))
            # print('total size: ', total_length, '--', title)

            chunk_size = 4096
            dl = 0
            shared_dict[title] = 0

            for block in response.iter_content(chunk_size):
                dl += len(block)
                f.write(block)
                done = int(50 * dl / total_length)
                shared_dict[title] = done

    except Exception as e:
        print('error with', title)
        os.remove(title)

    global n_workers
    with lock:
        n_workers -= 1


def report_status():
    import time

    global n_workers
    while n_workers != 0:
        os.system('cls')
        line = "\r"
        for title, done in shared_dict.items():
            line += "%s\n - [%s%s]\n" % (
                title, '=' * done, ' ' * (50 - done))
        line += '\n workers = ' + str(n_workers)
        sys.stdout.write(line)
        sys.stdout.flush()
        time.sleep(0.5)


threads = []
for json_url in mp3s:
    t = Thread(target=get_mp3_from_json_url, args=(json_url,))
    threads.append(t)
threads.append(Thread(target=report_status))

for t in threads:
    t.start()

for t in threads:
    t.join()
# https://greasyfork.org/zh-CN/scripts/24662-%E5%96%9C%E9%A9%AC%E6%8B%89%E9%9B%85%E9%9F%B3%E4%B9%90%E4%B8%8B%E8%BD%BD/code
