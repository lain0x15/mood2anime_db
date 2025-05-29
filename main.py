import requests
from pprint import pprint
import yaml

session = requests.Session()

data={
  "operationName": None,
  "variables": {},
  "query": '''{
        animes(limit: 60, page: 1, franchise: "gintama", kind: "!special", order: aired_on) {
            russian
            english
            name

            airedOn {year}
            releasedOn {year}
            score
            description
            poster { originalUrl }
            studios { name }
            kind
            franchise
            genres { russian }
        }
  }'''
}

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
   'content-type':'application/json'
}

r = session.post('https://shikimori.one/api/graphql', headers=headers, json=data)

for anime in r.json()['data']['animes']:
    print(f"{anime['russian']}\n\t{anime['english']}")