import urllib.request as req
from bs4 import BeautifulSoup
import xml.dom.minidom
from django.utils.feedgenerator import Rss201rev2Feed
from datetime import datetime
import locale
import html

def main():
    locale.setlocale(locale.LC_TIME, "C")
    url = 'https://docs.contrastsecurity.jp/ja/python-agent-release-notes-and-archive.html'
    res = req.urlopen(url)
    soup = BeautifulSoup(res, 'lxml')
    elems = soup.select('section.section.accordion')
    modified_date = soup.select_one('span.formatted-date').text.strip()

    feed = Rss201rev2Feed(
        title='Python Agent Release Note',
        link='https://contrastsecurity.dev/contrast-documentation-rss',
        description='Python Agent Release Note',
        language='ja',
        author_name="Contrast Security Japan G.K.",
        feed_url='https://contrastsecurity.dev/contrast-documentation-rss/python_rlsnote.xml',
        feed_copyright='Copyright 2023 Contrast Security Japan G.K.'
    )
    for elem in elems:
        try:
            id_str = elem.get("id")
            #pubdate_str = elem.get("data-publication-date") # November 6, 2023
            pubdate_str = elem.get("data-time-modified") # November 6, 2023
            pubdate = None
            if pubdate_str:
                pubdate = datetime.strptime(pubdate_str, '%B %d, %Y')
            title = elem.select('h3.title')[0].text.strip()
            if not title.lower().startswith('python'):
                continue
            #desc = elem.select('div.panel-body')[0].text
            desc_buffer = []
            #for elem2 in elem.select('p, div'):
            for elem2 in elem.select('p'):
                if elem2.parent.name == 'li':
                    desc_buffer.append('・%s' % elem2.text)
                else:
                    desc_buffer.append('%s' % elem2.text)
                #print(elem2.text)
            url = 'https://docs.contrastsecurity.jp/ja/python-agent-release-notes-and-archive.html#%s' % id_str
            feed.add_item(title=title, link=url, description=html.escape(''.join(['<p>{0}</p>'.format(s) for s in desc_buffer])), pubdate=pubdate)
        except IndexError:
            continue

    str_val = feed.writeString('utf-8')
    dom = xml.dom.minidom.parseString(str_val)
    with open('/feeds/python_rlsnote.xml','w') as fp:
        dom.writexml(fp, encoding='utf-8', newl='\n', indent='', addindent='    ')

if __name__ == "__main__":
    main()

