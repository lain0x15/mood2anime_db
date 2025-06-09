import requests, shutil, yaml, re
from pprint import pprint

def create_url(url_str):
    return re.sub('[^0-9a-zA-Z]+', '_', url_str)


session = requests.Session()

data={
  "operationName": None,
  "variables": {},
  "query": '''{
        animes(limit: 60, page: 1, franchise: "great_pretender", order: aired_on) {
            russian
            english
            name

            airedOn { year }
            releasedOn { year }
            score
            description
            poster { originalUrl }
            studios { name }
            kind
            franchise
            genres { russian }
            screenshots { originalUrl }
        }
  }'''
}

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
   'content-type':'application/json'
}

r = session.post('https://shikimori.one/api/graphql', headers=headers, json=data)

data = []

for anime in r.json()['data']['animes']:
    portraitImgName = f"{create_url(anime['name'])}{anime['poster']['originalUrl'][anime['poster']['originalUrl'].rfind('.'):]}"
    r = requests.get(anime['poster']['originalUrl'], stream=True)
    if r.status_code == 200:
        with open(f'animes/portraitImage/{portraitImgName}', 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)
    else:
        print(anime['poster']['originalUrl'])
        print(r.status_code)
    data.append({
        'url_name': create_url(anime['name']),
        'name': anime['russian'],
        'trailer': None,
        'releaseYear': anime['airedOn']['year'],
        'review': anime['score'],
        'description': anime['description'],
        'portraitImgName': portraitImgName,
        'studios': [studio['name'] for studio in anime['studios']],
        'typeName': anime['kind'],
        'franchise': anime['franchise'],
        'genres': [genre['russian'] for genre in anime['genres']]
    })

with open('test.yaml', 'w', encoding='utf-8') as file:
    yaml.dump(data, file, allow_unicode=True)