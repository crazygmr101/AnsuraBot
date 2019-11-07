def build(url, **kwargs):
    url += "?"
    ar = []
    for key, value in kwargs.items():
        ar.append(key + "=" + value)
    return url + "&".join(ar)