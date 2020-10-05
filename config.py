cfg = dict(
    regexs = {
"albums": r'href=\"\.\/albumarchive\/\d*?\/album\/(.*?)\" jsaction.*?>(?:<.*?>){5}(.*?)<\/div><.*?>(\d*?) ',
"photos": r'\],\"(https:\/\/lh\d\.googleusercontent\.com\/.*?)\",\[\"\d{21}\"(?:.*?,){16}\"(.*?)\"',
"review_loc_by_id": r'{}\",.*?\[\[null,null,(.*?),(.*?)\]'
},

headless = True, # if True, it doesn't show the browser while scraping GMaps reviews
ytb_hunt_always = False, # if True, search the Youtube channel everytime
gmaps_radius = 30, # in km. The radius distance to create groups of gmaps reviews.
gdocs_public_doc = "1jaEEHZL32t1RUN5WuZEnFpqiEPf_APYKrRBG9LhLdvE", # The public Google Doc to use it as an endpoint, to use Google's Search.
data_path = "resources/data.txt"
)