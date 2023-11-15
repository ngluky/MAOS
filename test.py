import httpx
from PIL import Image
import requests
from io import BytesIO

url = "https://media.valorant-api.com/weaponskinlevels/578e9077-4f88-260c-e54c-b988425c60e4/displayicon.png"

response = httpx.get(url)
img = Image.open(BytesIO(response.content))
print(img.mode)
img.show()