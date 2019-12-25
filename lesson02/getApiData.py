import requests;
import json;

url = 'https://n161.tech/api/dummyapi/user'
api_response = requests.get(url)
if api_response.status_code != 200:
    # This means something went wrong.
    raise ApiError('GET /tasks/ {}'.format(resp.status_code))
jsondata = api_response.json();
# debug --- print(jsondata);
for item in jsondata['data']:
    print("{} - {}".format(item['id'],item['firstName']));