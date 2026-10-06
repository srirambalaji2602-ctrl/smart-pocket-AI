import urllib.request


response = urllib.request.urlopen(
    "http://127.0.0.1:8000/health"
)


print(
    response
    .read()
    .decode()
)