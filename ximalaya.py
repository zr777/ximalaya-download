import requests
from bs4 import BeautifulSoup
from multiprocessing.dummy import Pool
import os

os.chdir(r'E:\python\2017_4_20')

mp3_url = 'http://www.ximalaya.com/2452186/album/4015467'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/57.0.2987.133'
}

res = requests.get(mp3_url, headers=headers)
soup = BeautifulSoup(res.content, 'lxml')
mp3_ids = soup.select_one('.personal_body').attrs['sound_ids']
json_url = 'http://www.ximalaya.com/tracks/{id}.json'
mp3s = [json_url.format(id=i) for i in mp3_ids.split(',')]


def get_mp3_from_json_url(json_url):
    mp3_info = requests.get(json_url, headers=headers).json()
    title = mp3_info['album_title'] + '+ ' + mp3_info['title'] + '.m4a'
    path = mp3_info['play_path']
    title = title.replace('|', '-')  # 避免特殊字符文件名异常

    if os.path.exists(title):
        return 'Already exists'

    # http://stackoverflow.com/questions/13137817/how-to-download-image-using-requests
    try:
        with open(title, 'wb') as f:
            response = requests.get(path, stream=True)

            if not response.ok:
                print('response error with', title)

            total_length = response.headers.get('content-length')
            print('total size: ', total_length, '--', title)

            chunk_size = 1024
            for block in response.iter_content(chunk_size):
                f.write(block)

            print('ok ---', title)

    except Exception as e:
        print('other error with', title)
        os.remove(title)


with Pool(10) as pool:
    pool.map(get_mp3_from_json_url, mp3s)

# https://greasyfork.org/zh-CN/scripts/24662-%E5%96%9C%E9%A9%AC%E6%8B%89%E9%9B%85%E9%9F%B3%E4%B9%90%E4%B8%8B%E8%BD%BD/code
