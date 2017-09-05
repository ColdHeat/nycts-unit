import requests

url = "https://api.trainsignapi.com/dev-logs/logs/29/upload"

querystring = {"clientId":"29"}

payload = ""

headers = {
    'content-type': "application/octet-stream",
    'x-api-key': "5lz8VPkVUL7gcjN5LsZwu1eArX8A3B2m8VeUfXxf"
    }

response = requests.request("POST", url, data=payload, headers=headers, params=querystring)

print(response.text)
