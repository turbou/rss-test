import urllib.request as req 
from bs4 import BeautifulSoup
import xml.dom.minidom
from django.utils.feedgenerator import Rss201rev2Feed
from datetime import datetime
import locale
import re

def main():
    url = 'https://docs.contrastsecurity.jp/ja/release.html'
    res = req.urlopen(url)
    soup = BeautifulSoup(res, 'lxml')
    elems = soup.select('section.section')
    modified_date = soup.select_one('span.formatted-date').text.strip()
    #print(modified_date)

    feed = Rss201rev2Feed(
        title='Contrast Release Note',
        link='https://contrastsecurity.dev/contrast-documentation-rss',
        description='Java Agent Release Note',
        language='ja',
        author_name="Contrast Security Japan G.K.",
        feed_url='https://contrastsecurity.dev/contrast-documentation-rss/contrast_rlsnote.xml',
        feed_copyright='Copyright 2023 Contrast Security Japan G.K.'
    )

    id_ptn = re.compile(r'^[0-9]{1,2}月-[0-9\-]+-$')
    title_ptn = re.compile(r'^[0-9]{1,2}月\([0-9\.]+\)$')

    for elem in elems:
        try:
            id_str = elem.get("id").strip()
            title = elem.select('h3.title')[0].text.strip()
            if not id_ptn.search(id_str) or not title_ptn.search(title):
                continue
            pubdate_str = elem.get("data-time-modified") # November 6, 2023
            pubdate = None
            if pubdate_str:
                pubdate = datetime.strptime(pubdate_str, '%B %d, %Y')
            #print(id_str, pubdate_str, title)
            desc_buffer = []
            for elem2 in elem.select('section.section'):
                id_str2 = elem2.get("id").strip()
                #print('- ', elem2.select_one('div.titlepage').text)
                desc_buffer.append('- %s' % elem2.select_one('div.titlepage').text)
                for elem3 in elem2.select('li.listitem'):
                    #print('  - ', elem3.select_one('p').text)
                    desc_buffer.append('  - %s' % elem3.select_one('p').text)
            #print(id_str, elem.get('data-legacy-id'))
            #if not title.lower().startswith('java'):
            #    continue
            url = 'https://docs.contrastsecurity.jp/ja/release.html#%s' % id_str
            feed.add_item(title=title, link=url, description=''.join(desc_buffer), pubdate=pubdate)
        except IndexError:
            continue
    str_val = feed.writeString('utf-8')
    dom = xml.dom.minidom.parseString(str_val)
    with open('/feeds/contrast_rlsnote.xml','w') as fp:
        dom.writexml(fp, encoding='utf-8', newl='\n', indent='', addindent='    ')

if __name__ == "__main__":
    main()

