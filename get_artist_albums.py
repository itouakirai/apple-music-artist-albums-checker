import requests
import json
import re
import os
import pandas as pd
from tqdm import tqdm
import concurrent.futures
from urllib.parse import unquote

#获取函数
def fetch_albums_and_songs(storefront):
    global albums_data, album_id_list

    url = f"https://amp-api.music.apple.com//v1/catalog/{storefront}/artists/{artist_id}/albums"
    while True:
        response = None
        flag404 = False
        while True:
            try:
                getresponse = requests.get(url, headers=headers)
                if getresponse.status_code == 200:
                    response = getresponse.json()
                    break
                elif getresponse.status_code == 404:
                    flag404 = True
                    break
            except requests.RequestException as e:
                print(f"Request {storefront} failed: {e}")
            #time.sleep(1)
        #response = requests.request("GET", url, headers=headers).json()
        if flag404:
            break
        for data in response["data"]:
            album_id = data["id"]
	  #计划添加的track_count
            track_count = data["attributes"]["trackCount"]
            album_name = data["attributes"]["name"]
            album_url = data["attributes"]["url"]
            upc = data["attributes"]["upc"]
            releaseDate = data["attributes"]["releaseDate"]
            if album_id not in album_id_list.keys():
                album_id_list[album_id] = storefront + '(' + str(track_count) + ')'
                albums_data[album_id] = ({'album_id': album_id, 'album_name': album_name, 'album_url': album_url, 'upc': upc, 'release_date': releaseDate, 'song': "False",'track_count': str(track_count)})
            else:
                album_id_list[album_id] = album_id_list[album_id] + ',' + storefront + '(' + str(track_count) + ')'
        try:
            url = "https://amp-api.music.apple.com/" + response["next"]
        except KeyError:
            break

    url = f"https://amp-api.music.apple.com//v1/catalog/{storefront}/artists/{artist_id}/songs"
    while True:
        response = None
        flag404 = False
        while True:
            try:
                getresponse = requests.get(url, headers=headers)
                if getresponse.status_code == 200:
                    response = getresponse.json()
                    break
                elif getresponse.status_code == 404:
                    flag404 = True
                    break
            except requests.RequestException as e:
                print(f"Request {storefront} failed: {e}")
            #time.sleep(1)
        #response = requests.request("GET", url, headers=headers).json()
        if flag404:
            break
        for data in response["data"]:
            album_name = data["attributes"]["albumName"]
            album_url = data["attributes"]["url"]
            track_count = data["attributes"]["trackCount"]
            upc = data["attributes"]["upc"]
            releaseDate = data["attributes"]["releaseDate"]
            pattern = re.compile(r'^(?:https:\/\/(?:beta\.music|music)\.apple\.com\/(\w{2})(?:\/album|\/album\/.+))\/(?:id)?(\d[^\D]+)(?:$|\?)')
            album_id = re.search(pattern, album_url).group(2)
            if album_id not in album_id_list.keys():
                #album_id_list.append(album_id)
                album_url = re.sub(r'\?i=\d+', '', album_url)
                album_id_list[album_id] = storefront + '(' + str(track_count) + ')'
                albums_data[album_id] = ({'album_id': album_id, 'album_name': album_name, 'album_url': album_url, 'upc': upc, 'release_date': releaseDate, 'song': "True",'track_count': str(track_count)})
            else:
                album_id_list[album_id] = album_id_list[album_id] + ',' + storefront + '(' + str(track_count) + ')'
        try:
            url = "https://amp-api.music.apple.com/" + response["next"]
        except KeyError:
            break

#获取输入的艺术家链接
url_o = input("Artist URL: ")

#定义国家代码集
storefronts = [
    'cn','us','hk','tw','jp','sg','kr',
    'ae', 'ag', 'ai', 'am', 'ao', 'ar', 'at', 'au', 'az', 'ba', 'bb', 'be', 'bg',
    'bh', 'bj', 'bm', 'bo', 'br', 'bs', 'bt', 'bw', 'by', 'bz', 'ca', 'cd', 'cg',
    'ch', 'ci', 'cl', 'cm', 'co', 'cr', 'cv', 'cy', 'cz', 'de', 'dk', 'dm', 'do',
    'dz', 'ec', 'ee', 'eg', 'es', 'fi', 'fj', 'fm', 'fr', 'ga', 'gb', 'gd', 'ge',
    'gh', 'gm', 'gr', 'gt', 'gw', 'gy', 'hn', 'hr', 'hu', 'id', 'ie', 'il', 'in',
    'iq', 'is', 'it', 'jm', 'jo', 'ke', 'kg', 'kh', 'kn', 'kw', 'ky', 'kz', 'la',
    'lb', 'lc', 'lk', 'lr', 'lt', 'lu', 'lv', 'ly', 'ma', 'md', 'me', 'mg', 'mk',
    'ml', 'mm', 'mn', 'mo', 'mr', 'ms', 'mt', 'mu', 'mv', 'mw', 'mx', 'my', 'mz',
    'na', 'ne', 'ng', 'ni', 'nl', 'no', 'np', 'nz', 'om', 'pa', 'pe', 'pg', 'ph',
    'pl', 'pt', 'py', 'qa', 'ro', 'rs', 'ru', 'rw', 'sa', 'sb', 'sc', 'se', 'si',
    'sk', 'sl', 'sn', 'sr', 'sv', 'sz', 'tc', 'td', 'th', 'tj', 'tm', 'tn', 'to',
    'tr', 'tt', 'tz', 'ua', 'ug', 'uy', 'uz', 'vc', 've', 'vg', 'vn', 'vu', 'xk',
    'ye', 'za', 'zm', 'zw'
]
#预处理艺术家链接
pattern = re.compile(r'https://music\.apple\.com/(\w{2})/(room|artist)(?:/([^/]+))?/(\d+)')
match = pattern.match(url_o)
if match:
    artist = unquote(match.group(3))
    artist_id = match.group(4)

    print("歌手:", artist)
    print("艺术家 ID:", artist_id)
else:
    print("URL 错误")

#定义请求头
headers = {
  'accept': '*/*',
  'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,ja;q=0.7,ru;q=0.6',
  'origin': 'https://music.apple.com',
  'referer': 'https://music.apple.com/',
  'sec-ch-ua': '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"Windows"',
  'sec-fetch-dest': 'empty',
  'sec-fetch-mode': 'cors',
  'sec-fetch-site': 'same-site',
  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
}

#获取JWT
home_page = requests.get("https://beta.music.apple.com", headers=headers).text
index_js_uri = re.search(r"/(assets/index-legacy-[^/]+\.js)", home_page).group(1)
index_js_page = requests.get(f"https://beta.music.apple.com/{index_js_uri}", headers=headers).text
token = re.search('(?=eyJh)(.*?)(?=")', index_js_page).group(1)
headers["authorization"] = 'Bearer ' + token
#定义列表
albums_data = {}
album_id_list = {}
#执行查询
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
    future_to_storefront = {executor.submit(fetch_albums_and_songs, storefront): storefront for storefront in storefronts}
    for future in tqdm(concurrent.futures.as_completed(future_to_storefront), total=len(storefronts), desc="检测"):
        continue
#合并字典
for album_id in album_id_list.keys():
    # 使用正则表达式提取所有的国家代码和数字
    matches = re.findall(r'([a-z]{2})\((\d+)\)', album_id_list[album_id])
    merged_data = {}
    for country, number in matches:
        number = int(number)
        if number in merged_data:
            merged_data[number].append(country)
        else:
            merged_data[number] = [country]
    all_same = len(merged_data) == 1 and 157 <= sum(len(countries) for countries in merged_data.values()) <= 167
    result = []
    if all_same:
        number = list(merged_data.keys())[0]
        all_countries = merged_data[number]
        remaining_countries = set(storefronts) - set(all_countries)
        if remaining_countries:
            remaining_string = ",".join(remaining_countries)
            result.append(f"({number})ALL-{remaining_string}")
        else:
            result.append(f"({number})ALL")
    else:
        # 将字典按数字从大到小排序
        sorted_data = sorted(merged_data.items(), key=lambda x: x[0], reverse=True)
            # 按要求格式化输出
        for number, countries in sorted_data:
            if len(countries) > 1:
                result.append(f"({number})" + ",".join(countries))
            else:
                result.append(f"({number})" + countries[0])

    # 输出结果
    final_result = ",".join(result)
    albums_data[album_id]['track_count'] = final_result
	
#输出文件
albums_data_values = albums_data.values()
albums_df = pd.DataFrame(albums_data_values)
sorted_albums_df = albums_df.sort_values(by=["upc", "release_date"])
with pd.ExcelWriter(f'{artist} - {artist_id}.xlsx', engine='xlsxwriter') as writer:
    sorted_albums_df.to_excel(writer, sheet_name='Sheet1', index=False)

    # 获取XlsxWriter workbook和worksheet对象
    workbook = writer.book
    worksheet = writer.sheets['Sheet1']

    # 设置列宽
    worksheet.set_column('A:A', 12)
    worksheet.set_column('B:B', 35)
    worksheet.set_column('C:C', 40)
    worksheet.set_column('D:D', 16)
    worksheet.set_column('E:E', 12)
    worksheet.set_column('F:F', 5)
    worksheet.set_column('G:G', 12)
#sorted_albums_df.to_excel(f'{artist} - {artist_id}.xlsx', index=False)
#sorted_albums_df.to_csv(f'{artist} - {artist_id}.csv', index=False)