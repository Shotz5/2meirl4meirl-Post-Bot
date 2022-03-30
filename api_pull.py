import requests
import json
import html

def main():
    api_url = "https://www.reddit.com/r/2meirl4meirl/hot/.json"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36"}
    res = requests.get(api_url, headers=headers)
    res_json = res.json()

    pictures = []

    for i in res_json["data"]["children"]:
        if "preview" in i["data"]:
            image_url = i["data"]["preview"]["images"][0]["source"]["url"]
            fixed_url = html.unescape(image_url)
            pictures.append(fixed_url)
    
    with open("data.json", "w+") as f:
        f.truncate(0)
        json.dump(res_json, f, indent=4)

    with open(pictures[0].split("/")[3].split(".")[0] + ".jpg", "wb") as f:
        f.write(requests.get(pictures[0]).content)

if __name__ == "__main__":
    main()