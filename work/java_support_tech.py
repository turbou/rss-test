import urllib.request as req 
from bs4 import BeautifulSoup
import xml.dom.minidom
from django.utils.feedgenerator import Rss201rev2Feed
from datetime import datetime
import locale
import re
import difflib
import shutil
import html
import hashlib

def main():
    url = 'https://docs.contrastsecurity.jp/ja/java-supported-technologies.html'
    res = req.urlopen(url)
    soup = BeautifulSoup(res, 'lxml')
    elems = soup.select('section.section')
    modified_date = soup.select_one('span.formatted-date').text.strip()

    feed = Rss201rev2Feed(
        title='Java Supported Technologies',
        link='https://contrastsecurity.dev/contrast-documentation-rss',
        description='Java Supported Technologies',
        language='ja',
        author_name="Contrast Security Japan G.K.",
        feed_url='https://contrastsecurity.dev/contrast-documentation-rss/java_support_tech_update.xml',
        feed_copyright='Copyright 2023 Contrast Security Japan G.K.'
    )

    write_flg = False
    item_dict = {}
    pubdate = None
    for elem in elems:
        try:
            if elem.parent.name == 'div':
                pubdate_str = elem.get("data-time-modified") # November 6, 2023
                if pubdate_str:
                    pubdate = datetime.strptime(pubdate_str, '%B %d, %Y')
                continue
            id_str = elem.get("id")
            id_hash = hashlib.md5(id_str.encode()).hexdigest()
            url = 'https://docs.contrastsecurity.jp/ja/java-supported-technologies.html#%s' % id_str
            guid = 'https://docs.contrastsecurity.jp/ja/java-supported-technologies.html#%s' % id_hash
            title = elem.select_one('h2.title').text
            text_buffer = []
            for elem2 in elem.select('p'):
                text_buffer.append(elem2.text)
            with open('/files/%s.tmp' % title,'w') as fp:
                fp.write('\n'.join(text_buffer))
            before_text = None
            with open('/files/%s.txt' % title,'r') as fp:
                before_text = fp.readlines()
            after_text = None
            with open('/files/%s.tmp' % title,'r') as fp:
                after_text = fp.readlines()
            res = difflib.unified_diff(before_text, after_text)
            res_str = '\n'.join(res)
            if (len(res_str.strip()) > 0):
                print('Found diff: ', title)
                item_dict[title] = (url, res_str, guid)
                shutil.move('/files/%s.tmp' % title, '/files/%s.txt' % title)
        except IndexError:
            continue

    if pubdate is None:
        pubdate = datetime.date.today()
    for k, v in item_dict.items():
        feed.add_item(title=k, link=v[0], description=''.join(['<p>{0}</p>'.format(s) for s in v[1].splitlines()]), pubdate=pubdate, unique_id=v[2])

    if len(item_dict) > 0:
        str_val = feed.writeString('utf-8')
        dom = xml.dom.minidom.parseString(str_val)
        with open('/feeds/java_support_tech_update.xml','w') as fp: 
            dom.writexml(fp, encoding='utf-8', newl='\n', indent='', addindent='    ')

if __name__ == "__main__":
    main()

