def feedify(url): # TODO: add https:// to the beginning ot http
      if 'feed' not in url and 'rss' not in url:
         if url[-1] == '/':
            url = url + 'feed/'
         else:
            url += '/feed/'
      if 'http' not in url:
         url = 'https://' + url
      return url