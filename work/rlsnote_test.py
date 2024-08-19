import urllib.request as req
from bs4 import BeautifulSoup
import xml.dom.minidom
from django.utils.feedgenerator import Rss201rev2Feed
import datetime
import locale
import html
import hashlib
import os

def main():
    locale.setlocale(locale.LC_TIME, "C")

    feed = Rss201rev2Feed(
        title='Release Note Test',
        link='https://turbou.github.io/rss-test',
        description='Release Note Test',
        language='ja',
        author_name="turbou",
        feed_url='https://turbou.github.io/rss-test/rlsnote_test.xml',
        feed_copyright='Copyright 2024 turbou'
    )
    rlsnote_count = os.getenv('RLSNOTE_COUNT')
    rlsnote_start = os.getenv('RLSNOTE_START')
    start_date = datetime.datetime.strptime(rlsnote_start, '%Y-%m-%d')
    
    for idx in range(int(rlsnote_count)):
        try:
            id_str = str(idx).zfill(10)
            pubdate = start_date + datetime.timedelta(days=idx)
            title = id_str
            desc_buffer = []
            for idx2 in range(3):
                desc_buffer.append(id_str)
            id_hash = hashlib.md5(id_str.encode()).hexdigest()
            url = 'https://docs.contrastsecurity.jp/ja/java-agent-release-notes-and-archive.html'
            guid = 'https://docs.contrastsecurity.jp/ja/java-agent-release-notes-and-archive.html#%s' % id_hash
            feed.add_item(title=title, link=url, description=''.join(['<p>{0}</p>'.format(s) for s in desc_buffer]), pubdate=pubdate, unique_id=guid)
        except IndexError:
            continue

    str_val = feed.writeString('utf-8')
    dom = xml.dom.minidom.parseString(str_val)
    with open('/feeds/rlsnote_test.xml','w') as fp:
        dom.writexml(fp, encoding='utf-8', newl='\n', indent='', addindent='    ')

if __name__ == "__main__":
    main()

