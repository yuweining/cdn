import requests

print(requests.get('https://cuojue.org/not-exists/be4b3658-2045-4468-8530-cc11c2145849', verify=False).text)
