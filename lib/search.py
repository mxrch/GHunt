import httpx
import json
from pprint import pprint

def search(query, cfg):
	cookies = ""
	token = ""
	with open(cfg['data_path'], 'r') as f:
		out = json.loads(f.read())
		token = out["keys"]["gdoc"]
		cookies = out["cookies"]

	doc = cfg["gdocs_public_doc"]
	size = 1000

	data = {"request": '["documentsuggest.search.search_request","{}",[{}],null,1]'.format(query, size)}

	req = httpx.post('https://docs.google.com/document/d/{}/explore/search?token={}'.format(doc, token), cookies=cookies, data=data)
	if req.status_code != 200:
		print("Error : request gives {}".format(req.status_code))
		exit()

	output = json.loads(req.text.replace(")]}'", ""))
	#pprint(output)

	results = []
	for result in output[0][1]:
		link = result[0][0]
		title = result[0][1]
		desc = result[0][2]
		results.append({"title": title, "desc": desc, "link": link})

	return results
