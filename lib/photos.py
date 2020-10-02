import httpx
import re
from io import BytesIO
from lib.metadata import ExifEater
from PIL import Image


def gpics(gaiaID, client, cfg):
	baseurl = "https://get.google.com/albumarchive/"

	print(f"\nGoogle Photos : {baseurl + gaiaID}")
	req = client.get(baseurl + gaiaID)
	results = re.compile(cfg["regexs"]["albums"]).findall(req.text)

	list_albums_length = len(results)

	if results:
		exifeater = ExifEater()
		pics = []
		for album in results:
			album_name = album[1]
			album_link = baseurl + gaiaID + "/album/" + album[0]
			album_length = int(album[2])

			if album_length >= 1:
				req = client.get(album_link)
				source = req.text.replace('\n', '')
				open('tmp.html', 'w').write(source)
				results_pics = re.compile(cfg["regexs"]["photos"]).findall(source)
				for pic in results_pics:
					pic_name = pic[1]
					pic_link = pic[0]
					pics.append(pic_link)
		
		print(f"=> {list_albums_length} albums{', '+str(len(pics))+' photos' if list_albums_length else ''}")
		for pic in pics:
			req = client.get(pic)
			img = Image.open(BytesIO(req.content))
			exifeater.feed(img)

		print("\nSearching metadata...")
		exifeater.output()
	else:
		print("=> No album")