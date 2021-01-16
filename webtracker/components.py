def get_url_combo(url):
    has_http = 'http' in url
    is_feed = 'feed' in url or 'rss' in url

    if url[-1] != '/':
        url += '/'

    if has_http and is_feed:
        return [url]

    combs = [url]
    if not has_http:
        for c in combs:
            combs.append('http://' + c)
            combs.append('https://' + c)
    if not is_feed:
        for c in combs:
            combs.append(c + 'feed/')
            combs.append(c + 'rss/')
    return combs

def strip(url):
    if http in url:
        url = url.split('://')[-1]

    if 'feed' in url:
        return url[:-5]
    elif 'rss' in url:
        return url[:-4]
    else:
        raise "Can't strip url"
