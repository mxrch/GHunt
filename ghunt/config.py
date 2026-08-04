headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; rv:68.0) Gecko/20100101 Firefox/68.0',
    'Connection': 'Keep-Alive'
}

android_headers = {
    'User-Agent': '{}/323710070 (Linux; U; Android 11; fr_FR; Pixel 5; Build/RD2A.211001.002; Cronet/97.0.4692.70) grpc-java-cronet/1.44.0-SNAPSHOT', # android package name
    'Connection': 'Keep-Alive'
}

templates = {
    "gmaps_pb":{
        "stats": "!1s{}!2m3!1sYE3rYc2rEsqOlwSHx534DA!7e81!15i14416!6m2!4b1!7b1!9m0!16m4!1i100!4b1!5b1!6BQ0FFU0JrVm5TVWxEenc9PQ!17m28!1m6!1m2!1i0!2i0!2m2!1i458!2i736!1m6!1m2!1i1868!2i0!2m2!1i1918!2i736!1m6!1m2!1i0!2i0!2m2!1i1918!2i20!1m6!1m2!1i0!2i716!2m2!1i1918!2i736!18m12!1m3!1d806313.5865720833!2d150.19484835!3d-34.53825215!2m3!1f0!2f0!3f0!3m2!1i1918!2i736!4f13.1",
        "reviews": {
            "first": "!1s{}!2m3!1s_2zAZ5CJDouBi-gPpJ7biAg!7e81!15i14416!6m2!4b1!7b1!9m0!17m28!1m6!1m2!1i0!2i0!2m2!1i530!2i1279!1m6!1m2!1i3390!2i0!2m2!1i3440!2i1279!1m6!1m2!1i0!2i0!2m2!1i3440!2i20!1m6!1m2!1i0!2i1259!2m2!1i3440!2i1279!18m15!1m3!1d2834470.167608874!2d150.05636185!3d-33.57307085!2m3!1f0!2f0!3f0!3m2!1i3440!2i1279!4f13.1!6m2!1f0!2f0!41m15!1i20!2m9!2b1!3b1!5b1!7b1!12m4!1b1!2b1!4m1!1e1!3sCAESA0VnQQ%3D%3D!7m2!1m1!1e1",
            "page": "!1s{}!2m3!1s_2zAZ5CJDouBi-gPpJ7biAg!7e81!15i14416!6m2!4b1!7b1!9m0!17m28!1m6!1m2!1i0!2i0!2m2!1i530!2i1279!1m6!1m2!1i3390!2i0!2m2!1i3440!2i1279!1m6!1m2!1i0!2i0!2m2!1i3440!2i20!1m6!1m2!1i0!2i1259!2m2!1i3440!2i1279!18m15!1m3!1d2834470.167608874!2d150.05636185!3d-33.57307085!2m3!1f0!2f0!3f0!3m2!1i3440!2i1279!4f13.1!6m2!1f0!2f0!41m15!1i20!2m9!2b1!3b1!5b1!7b1!12m4!1b1!2b1!4m1!1e1!3s{}!7m2!1m1!1e1"
        },
        "photos": {
            "first": "!1s{}!2m3!1spQUAYoPQLcOTlwT9u6-gDA!7e81!15i18404!9m0!14m69!1m57!1m4!1m3!1e3!1e2!1e4!3m5!2m4!3m3!1m2!1i260!2i365!4m1!3i10!10b1!11m42!1m3!1e1!2b0!3e3!1m3!1e2!2b1!3e2!1m3!1e2!2b0!3e3!1m3!1e8!2b0!3e3!1m3!1e10!2b0!3e3!1m3!1e10!2b1!3e2!1m3!1e9!2b1!3e2!1m3!1e10!2b0!3e3!1m3!1e10!2b1!3e2!1m3!1e10!2b0!3e4!2b1!4b1!2m5!1e1!1e4!1e3!1e5!1e2!3b1!4b1!5m1!1e1!7b1",
            "page": "!1s{}!2m3!1spQUAYoPQLcOTlwT9u6-gDA!7e81!15i14415!9m0!14m68!1m58!1m4!1m3!1e3!1e2!1e4!3m5!2m4!3m3!1m2!1i260!2i365!4m2!2s{}!3i100!10b1!11m42!1m3!1e1!2b0!3e3!1m3!1e2!2b1!3e2!1m3!1e2!2b0!3e3!1m3!1e8!2b0!3e3!1m3!1e10!2b0!3e3!1m3!1e10!2b1!3e2!1m3!1e9!2b1!3e2!1m3!1e10!2b0!3e3!1m3!1e10!2b1!3e2!1m3!1e10!2b0!3e4!2b1!4b1!2m5!1e1!1e4!1e3!1e5!1e2!5m1!1e1!7b1!17m28!1m6!1m2!1i0!2i0!2m2!1i458!2i595!1m6!1m2!1i950!2i0!2m2!1i1000!2i595!1m6!1m2!1i0!2i0!2m2!1i1000!2i20!1m6!1m2!1i0!2i575!2m2!1i1000!2i595!18m12!1m3!1d1304345.2752527467!2d149.32871599857805!3d-34.496155324132545!2m3!1f0!2f0!3f0!3m2!1i1000!2i595!4f13.1"
        }
    }
}

gmaps_radius     = 30 # in km. The radius distance to create groups of gmaps reviews.

# Cookies
default_consent_cookie = "YES+cb.20220118-08-p0.fr+FX+510"
default_pref_cookie = "tz=Europe.Paris&f6=40000000&hl=en" # To set the lang settings to english

# Page opened in Firefox when using the Companion login (listening mode)
login_companion_url = "https://accounts.google.com"