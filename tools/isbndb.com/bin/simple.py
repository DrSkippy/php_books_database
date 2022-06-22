import requests as req
import json
 
with open("./config/config.json", "r") as infile:
    config = json.load(infile)

print("Enter s to stop")
h = {'Authorization': config["key"]}
ans = None
while ans is None:
    ans = input("Enter isbn13: ")
    if not ans.startswith("s"):
        url = config["url_isbn"].format(ans)
        resp = req.get(url, headers=h)
        print(json.dumps(resp.json(), indent=4, sort_keys=True))
        ans = None
