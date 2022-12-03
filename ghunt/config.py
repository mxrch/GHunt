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
            "first": "!1s{}!2m5!1soViSYcvVG6iJytMPk6amiA8%3A1!2zMWk6NCx0OjE0MzIzLGU6MCxwOm9WaVNZY3ZWRzZpSnl0TVBrNmFtaUE4OjE!4m1!2i14323!7e81!6m2!4b1!7b1!9m0!10m6!1b1!2b1!5b1!8b1!9m1!1e3!14m69!1m57!1m4!1m3!1e3!1e2!1e4!3m5!2m4!3m3!1m2!1i260!2i365!4m1!3i10!10b1!11m42!1m3!1e1!2b0!3e3!1m3!1e2!2b1!3e2!1m3!1e2!2b0!3e3!1m3!1e8!2b0!3e3!1m3!1e10!2b0!3e3!1m3!1e10!2b1!3e2!1m3!1e9!2b1!3e2!1m3!1e10!2b0!3e3!1m3!1e10!2b1!3e2!1m3!1e10!2b0!3e4!2b1!4b1!2m5!1e1!1e4!1e3!1e5!1e2!3b0!4b1!5m1!1e1!7b1!16m3!1i10!4b1!5b1!17m0!18m9!1m3!1d2567.508024970022!2d-78.667885!3d35.7546725!2m0!3m2!1i537!2i609!4f13.1",
            "page": "!1s{}!2m3!1sYE3rYc2rEsqOlwSHx534DA!7e81!15i14416!6m2!4b1!7b1!9m0!16m4!1i100!4b1!5b1!6B{}!17m28!1m6!1m2!1i0!2i0!2m2!1i458!2i736!1m6!1m2!1i1868!2i0!2m2!1i1918!2i736!1m6!1m2!1i0!2i0!2m2!1i1918!2i20!1m6!1m2!1i0!2i716!2m2!1i1918!2i736!18m12!1m3!1d806313.5865720833!2d150.19484835!3d-34.53825215!2m3!1f0!2f0!3f0!3m2!1i1918!2i736!4f13.1"
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