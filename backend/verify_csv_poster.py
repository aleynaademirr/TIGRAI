import requests

def check_url(url):
    try:
        r = requests.head(url, timeout=5)
        print(f"URL: {url} -> Status: {r.status_code}")
    except Exception as e:
        print(f"URL: {url} -> Error: {e}")

# Toy Story
check_url("https://image.tmdb.org/t/p/original/rhIRbceoE9lR4veEXuwCC2wARtG.jpg")
# GoldenEye
check_url("https://image.tmdb.org/t/p/original/5c0ovjT41KnYIHYuF4AWsTe3sKh.jpg")
