import httpx

def download_file(url, filepath, headers, headers2):
    with httpx.Client(headers=headers) as client:
        response = client.get(url)
    print(response)
    print(response.headers['location'])

    with httpx.stream("GET", url=f'{response.headers["location"]}', headers=headers2) as response:
        print(response)
        with open(filepath, "wb") as file:
            for chunk in response.iter_raw():
                file.write(chunk)

# url = 'https://s3.amazonaws.com/tsinternal_standard/Internal/2022/10/16__10_50_25/Sofa_Set_01.fbx68AD3BC5-44A9-45D0-A2AB-232546E89E33.fbx?response-content-disposition=attachment;filename="Sofa_Set_01.fbx"&AWSAccessKeyId=AKIAIJ6EELKKOTA5UAUA&Expires=1685399793&Signature=Hb03tRs8eCkhmF2FWhGVKJpNUe4='
filepath = "file"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0',
    'Cookie': '_gcl_aw=GCL.1684411432.Cj0KCQjwmZejBhC_ARIsAGhCqnd6jY1nIajjrtuVcbbey33K9_fBDaUWFZXL0zt4ll9u_V5giDC5PiMaAt-hEALw_wcB; _gcl_dc=GCL.1684411432.Cj0KCQjwmZejBhC_ARIsAGhCqnd6jY1nIajjrtuVcbbey33K9_fBDaUWFZXL0zt4ll9u_V5giDC5PiMaAt-hEALw_wcB; _gcl_au=1.1.59657227.1684411430; M=976641AD-D617-4C3F-B4EF-CB52AA86473E; M20UR15=%7B%22s%22%3A%226F48B420-3075-46F4-AAD3-C29B35589AFA%22%2C%22csrf%22%3A%222124086B892809C429172E0E21C7EC6D3E49D9DA%22%2C%22d%22%3A%222023-05-29T22%3A14%3A56Z%22%2C%22email%22%3A%22naruoutlet%40gmail.com%22%2C%22industry%22%3A%22Game%20Developer%20-%20PC%2FConsole%2FMobile%22%2C%22application%22%3A%223ds%20Max%22%2C%22engine%22%3A%22Unity%22%2C%22clnt%22%3A%221%22%2C%22name%22%3A%22KM-member3536253678%22%7D; SnapABugHistory=1#; _clck=us10gz|2|fc0|0|1233; _ga=GA1.2.562640225.1684411434; _gac_UA-227915-1=1.1684411434.Cj0KCQjwmZejBhC_ARIsAGhCqnd6jY1nIajjrtuVcbbey33K9_fBDaUWFZXL0zt4ll9u_V5giDC5PiMaAt-hEALw_wcB; __ssid=d3121d7e9a4a168168c767500e06367; _hp2_props.3723677730=%7B%22suggestions_version%22%3A%221%22%2C%22Logged%20In%22%3A%22true%22%7D; _hp2_id.3723677730=%7B%22userId%22%3A%222228312631936433%22%2C%22pageviewId%22%3A%22652100749714266%22%2C%22sessionId%22%3A%221806381622831782%22%2C%22identity%22%3A%22KM-member3536253678%22%2C%22trackerVersion%22%3A%224.0%22%2C%22identityField%22%3Anull%2C%22isIdentified%22%3A1%7D; RDDisplayFilter=%7B%22sort_column%22%3A%22null%22%2C%22sort_order%22%3A%22null%22%2C%22page_size%22%3A%22500%22%7D; blOpenedAccordion=true; _gaexp=GAX1.2.SNZDkz_8Q9mdK2o-StOSYQ.19589.0!siH7jPeaSTWjI9V3wjuEGA.19594.1; stck_anonymous_id=099e2325-0b22-43d2-834d-b5b61fbf0d25; sstk_anonymous_id=099e2325-0b22-43d2-834d-b5b61fbf0d25; ajs_anonymous_id=099e2325-0b22-43d2-834d-b5b61fbf0d25; _hp2_id.2323688811=%7B%22userId%22%3A%225113691552135178%22%2C%22pageviewId%22%3A%222153910490952699%22%2C%22sessionId%22%3A%22813213081069129%22%2C%22identity%22%3Anull%2C%22trackerVersion%22%3A%224.0%22%7D; cfid=7167a9aa-3f6c-4845-a12f-c25cdbbd7d00; cftoken=0; _M20UR15=B6CB403AEB6E78167DD24EF0AFE9329C; OSD=%7B%22eligible_cart%22%3A0%2C%22code%22%3A%22%22%7D; _gid=GA1.2.364080630.1685129153; SnapABugVisit=170#1684411432; _turbosquid_rails_session=khvzQMhlO2mgrMthu4%2F3NkkFvSNyo7n5iFS3MzLxb0n8WBT8BVmtEHqmFNNp%2BDaoNrvWgLeB18dPzKWGLcRMAEbfgMszwgv6l%2Fu3btYETpMz3xD8nv2qG%2B7RCsAqQcl%2Bxm073bAxWwWrCcpVmAGz1vF80Cyghf8xjp5fwZaIlzoxmcIsGZkv%2FQVC9qZqOw8UotMLTd5dmKmPkAC54ZG%2BaOngKx7IhBjBktwQ1M4w4fzjJDKZBUNJrfAF3alBV48E%2BeJYNAX0S8VuD5zCKmiT%2FcNFWwDKbb8tD%2F28VEyTcqo9--PW6ekXFm1lueYlBr--oeMwWyEaQjv3CjFQWLRXDA%3D%3D; SnapABugRef=https%3A%2F%2Fwww.turbosquid.com%2FAssetManager%2FDownloads%3FblDownloadError%3DTRUE%26intErrorFileItemID%3D1973705%20; SnapABugUserAlias=%23; _uetsid=160e30a0fbfb11edb50627d8c5f34104; _uetvid=0e1580b0f57411eda91d87593b61303a; _hp2_ses_props.3723677730=%7B%22z%22%3A1%2C%22r%22%3A%22https%3A%2F%2Fwww.turbosquid.com%2F3d-models%2F3d-model-sofa-set-01-1973705%22%2C%22ts%22%3A1685399673570%2C%22d%22%3A%22www.turbosquid.com%22%2C%22h%22%3A%22%2FAssetManager%2FIndex.cfm%22%2C%22t%22%3A%22TurboSquid%20--%20My%20Files%22%2C%22q%22%3A%22%3FstgAction%3DgetFiles%26subAction%3DDownload%26intID%3D1973705%26intType%3D3%26csrf%3D2124086B892809C429172E0E21C7EC6D3E49D9DA%26showDownload%3D1%26s%3D1%22%7D'

}

headers2 = {
    'Host': 's3.amazonaws.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'cross-site',
    'Sec-Fetch-User': '?1'
}

url = 'https://www.turbosquid.com/Download/1973705_65854019'

download_file(url, filepath=filepath, headers=headers, headers2=headers2)