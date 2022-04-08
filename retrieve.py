import os
import json
import urllib.request
import urllib.parse


BEARER_TOKEN = os.environ['BEARER_TOKEN']
API_DOMAIN = 'api.twitter.com'
WEBSITES = (
    ('lethain.txt', 'lethain.com -from:lethain_bot -RT'),
    ('staffeng.txt', 'staffeng.com -RT'),
    ('infraeng.txt', 'infraeng.dev -RT'),
)


def query_website(query, max_results=50):
    # minimum max_results is 10 or api rejects...
    if max_results < 10:
        max_results = 10

    params = {
        'query': query,
        'expansions': 'author_id',
        'tweet.fields': 'id,author_id,entities',
        'max_results': max_results,
        'sort_order': 'recency',
    }
    url = "https://" + API_DOMAIN + "/2/tweets/search/recent?%s" % urllib.parse.urlencode(params)
    headers = {
        'Authorization': 'Bearer %s' % (BEARER_TOKEN,),
    }
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as resp:
        return resp.read()

def parse_results(results):
    parsed = json.loads(results)
    data = parsed['data']
    users = parsed['includes']['users']

    user_lookup = {}
    for user in users:
        user_id = user['id']
        user_lookup[user_id] = user['username']

    txt = ""
    for tweet in data:
        author_id = tweet['author_id']
        if len(txt) > 0:
            txt += "---------\n"
        txt += 'author: %s\n' % user_lookup[author_id]
        txt += "%s\n\n" % tweet['text']
        if 'entities' in tweet:
            entities = tweet['entities']
            if 'urls' in entities:
                urls = entities['urls']
                for url in urls:
                    txt += "url: %s\n" % url['expanded_url']

        txt += "https://twitter.com/%s/status/%s\n" % (user_lookup[author_id], tweet['id'])
    return txt


def main():
    for dest_filename, website in WEBSITES:
        results = query_website(website, max_results=3)
        parsed = parse_results(results)
        with open(dest_filename, 'w') as fout:
            fout.write(parsed)


if __name__ == "__main__":
    main()
