import json
import httpx

from pprint import pprint


def search(query, data_path, gdocs_public_doc, size=1000):
    cookies = ""
    token = ""

    with open(data_path, 'r') as f:
        out = json.loads(f.read())
        token = out["keys"]["gdoc"]
        cookies = out["cookies"]
    data = {"request": '["documentsuggest.search.search_request","{}",[{}],null,1]'.format(query, size)}
    req = httpx.post('https://docs.google.com/document/d/{}/explore/search?token={}'.format(gdocs_public_doc, token),
                     cookies=cookies, data=data)
    if req.status_code != 200:
        exit("Error (GDocs): request gives {}".format(req.status_code))

    output = json.loads(req.text.replace(")]}'", ""))
    #pprint(output)
    if isinstance(output[0][1], str) and output[0][1].lower() == "xsrf":
        exit(f"\n[-] Error : XSRF detected.\nIt means your cookies have expired, please generate new ones.")

    results = []
    for result in output[0][1]:
        link = result[0][0]
        title = result[0][1]
        desc = result[0][2]
        results.append({"title": title, "desc": desc, "link": link})

    return results
