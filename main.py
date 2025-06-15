import requests, shutil, yaml, re, time, hashlib
from datetime import datetime

def create_url(url_str):
    return re.sub('[^0-9a-zA-Z]+', '_', url_str)

session = requests.Session()
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
    'content-type':'application/json'
}

if __name__ == '__main__':
    with open(f'franchises/main.yml') as f:
        franchises = yaml.safe_load(f)
        for franchise in franchises:
            data={
              "operationName": None,
              "variables": {},
              "query": '''{
                    animes(limit: 60, page: 1, franchise: "''' + franchise + '''", order: aired_on) {
                        russian
                        english
                        name

                        airedOn { year }
                        releasedOn { year }
                        score
                        descriptionHtml
                        poster { originalUrl }
                        studios { name }
                        kind
                        episodes
                        franchise
                        genres {
                            russian
                            kind
                        }
                        screenshots { originalUrl }
                    }
              }'''
            }
            r = session.post('https://shikimori.one/api/graphql', headers=headers, json=data)
            data = []
            for anime in r.json()['data']['animes']:
                portraitImgName = f"{create_url(anime['name'])}{anime['poster']['originalUrl'][anime['poster']['originalUrl'].rfind('.'):]}"
                r = session.get(anime['poster']['originalUrl'], headers=headers, stream=True)
                if r.status_code == 200:
                    with open(f'animes/portraitImage/{portraitImgName}', 'wb') as f:
                        r.raw.decode_content = True
                        shutil.copyfileobj(r.raw, f)
                else:
                    print(anime['poster']['originalUrl'])
                    print(r.status_code)
                for idx, screenshot in enumerate(anime['screenshots']):
                    r = session.get(screenshot['originalUrl'], headers=headers, stream=True)
                    if idx == 4:
                        break
                    if r.status_code == 200:
                        file_extention = f"{screenshot['originalUrl'][screenshot['originalUrl'].rfind('.'):screenshot['originalUrl'].rfind('?')]}"
                        with open(f'animes/screenshots/{create_url(anime['name'])}_{idx}{file_extention}', 'wb') as f:
                            r.raw.decode_content = True
                            shutil.copyfileobj(r.raw, f)
                    else:
                        print(screenshot['originalUrl'])
                        print(r.status_code)

                type_handler={
                    'tv': 'Сериал',
                    'movie': 'Фильм',
                    'ova': 'OVA',
                    'ona': 'ONA',
                    'special': 'Спецвыпуск',
                    'tv_special': 'TV Спецвыпуск',
                    'music': 'Клип',
                    'pv': 'Проморолик',
                    'cm': 'Реклама'
                }
                data.append({
                    'url_name': create_url(anime['name'] + '_' + hashlib.md5(anime['name'].encode()).hexdigest()[:5]),
                    'name': anime['russian'],
                    'releaseYear': datetime(anime['airedOn']['year'], 1, 1, 0, 0, 0),
                    'review': anime['score'],
                    'description': re.sub(r"<.+?>", "", anime['descriptionHtml']) if anime['descriptionHtml'] else None,
                    'portraitImgName': portraitImgName,
                    'studios': [studio['name'] for studio in anime['studios']],
                    'typeName': type_handler[anime['kind']],
                    'episodes': anime['episodes'] if anime['episodes'] > 1 else None,
                    'franchise': anime['franchise'],
                    'genres': [genre['russian'] for genre in anime['genres'] if genre['kind'] in ['genre','demographic']],
                    'screenshots': [
                        f"{create_url(anime['name'])}_{idx}{screenshot['originalUrl'][screenshot['originalUrl'].rfind('.'):screenshot['originalUrl'].rfind('?')]}" for idx, screenshot in enumerate(anime['screenshots']) if idx < 4
                    ]
                })
            with open(f'animes/{franchise}.yml', 'w', encoding='utf-8') as file:
                yaml.dump(data, file, allow_unicode=True)