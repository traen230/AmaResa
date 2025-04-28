import requests
from PIL import Image
import imagehash
from io import BytesIO

# 対象画像URL
url = "https://m.media-amazon.com/images/I/71PAJwm38ZL._AC_SL1500_.jpg"

# 画像を取得し、pHash計算
response = requests.get(url)
img = Image.open(BytesIO(response.content))
phash = imagehash.phash(img)

print("この画像のpHashは:", phash)
