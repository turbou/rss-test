import urllib.request as req
from bs4 import BeautifulSoup
import xml.dom.minidom
from django.utils.feedgenerator import Rss201rev2Feed
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta
import datetime
import locale
import html
import hashlib
import os
import json
import time
import re

CONTRAST_AGENT_INFOS = [
     {
         'language': '.NET Core',
         'doc_url': 'https://docs.contrastsecurity.jp/ja/-net-core-agent-release-notes-and-archive.html',
         'check_word': '.net',
     }, {
         'language': '.NET Framework',
         'doc_url': 'https://docs.contrastsecurity.jp/ja/-net-framework-agent-release-notes-and-archive.html',
         'check_word': '.net',
     }, {
         'language': 'Go',
         'doc_url': 'https://docs.contrastsecurity.jp/ja/go-agent-release-notes-and-archive.html',
         'check_word': 'go',
     }, {
         'language': 'Java',
         'doc_url': 'https://docs.contrastsecurity.jp/ja/java-agent-release-notes-and-archive.html',
         'check_word': 'java',
     }, {
         'language': 'NodeJS',
         'doc_url': 'https://docs.contrastsecurity.jp/ja/node-js-agent-release-notes-and-archive.html',
         'check_word': 'node',
     }, {
         'language': 'PHP',
         'doc_url': 'https://docs.contrastsecurity.jp/ja/php-agent-release-notes-and-archive.html',
         'check_word': 'php',
     }, {
         'language': 'Python',
         'doc_url': 'https://docs.contrastsecurity.jp/ja/python-agent-release-notes-and-archive.html',
         'check_word': 'python',
     }, {
         'language': 'Ruby',
         'doc_url': 'https://docs.contrastsecurity.jp/ja/ruby-agent-release-notes-and-archive.html',
         'check_word': 'ruby',
     },
]

def main():
    locale.setlocale(locale.LC_TIME, "C")
    path = '/files/agent_rlsdate.json'
    versions_dict = {}
    if os.path.isfile(path):
        with open(path) as f:
            versions_dict = json.load(f)
    
    for agent_info in CONTRAST_AGENT_INFOS:
        #print(agent_info['language'], agent_info['doc_url'])
        res = req.urlopen(agent_info['doc_url'])
        soup = BeautifulSoup(res, 'lxml')
        elems = soup.select('section.section.accordion')
        for elem in elems:
            try:
                id_str = elem.get("id")
                pubdate_str = elem.get("data-time-modified") # November 6, 2023
                pubdate = None
                if pubdate_str:
                    pubdate = dt.strptime(pubdate_str, '%B %d, %Y')
                title = elem.select('h3.title')[0].text.strip()
                if not title.lower().startswith(agent_info['check_word']):
                    continue
                desc_buffer = []
                for elem2 in elem.select('p'):
                    if elem2.parent.name == 'li':
                        desc_buffer.append('・%s' % elem2.text)
                    else:
                        desc_buffer.append('%s' % elem2.text)
                id_hash = hashlib.md5(id_str.encode()).hexdigest()
                description = ''.join(desc_buffer)
                rls_date = None
                if 'リリース日' in description:
                    m = re.search('リリース日[^2]+([0-9]{4})年([0-9]{1,2})月([0-9]{1,2})日', description)
                    if m is None:
                        continue
                    rls_date = dt(int(m.group(1)), int(m.group(2)), int(m.group(3)))
                elif 'Release date' in description:
                    m = re.search('Release date[^A-Z]+(([A-Za-z]+) ([0-9]{1,2}), ([0-9]{4}))', description)
                    if m is None:
                        continue
                    rls_date = dt.strptime(m.group(1), '%B %d, %Y')
                if rls_date:
                    versions_dict[title] = (rls_date.strftime('%Y%m%d%H%M%S'), agent_info['doc_url'], id_hash)
            except IndexError:
                continue
        time.sleep(1)

    feed = Rss201rev2Feed(
        title='End of Agent support',
        link='https://contrastsecurity.dev/contrast-documentation-rss',
        description='End Of Agent Support',
        language='ja',
        author_name="Contrast Security Japan G.K.",
        feed_url='https://contrastsecurity.dev/contrast-documentation-rss/end_of_support.xml',
        feed_copyright='Copyright 2024 Contrast Security Japan G.K.'
    )

    today = dt.today().replace(hour=0, minute=0, second=0, microsecond=0)
    env_today = os.getenv('TODAY')
    if env_today:
        today = dt.strptime(env_today, '%Y-%m-%d').replace(hour=0, minute=0, second=0, microsecond=0)
        print('using env.TODAY %s' % today)
    item_dict = {}
    for title, data_tuple in versions_dict.items():
        rls_date = dt.strptime(data_tuple[0], '%Y%m%d%H%M%S')
        date_end_of_support = rls_date + relativedelta(years=1)
        date_end_of_support = date_end_of_support - datetime.timedelta(days=1)
        date_before_30days = date_end_of_support - datetime.timedelta(days=30)
        #print(title, rls_date, today, date_end_of_support, date_before_30days)
        if today == date_before_30days:
            item_dict[title] = (data_tuple[1], '%s エージェントのサポート終了から30日前です。' % title, data_tuple[2])
        if today == date_end_of_support:
            item_dict[title] = (data_tuple[1], '%s エージェントのサポート終了日となります。' % title, data_tuple[2])

    pubdate = pubdate
    pub_date_str = os.getenv('PUB_DATE')
    if pub_date_str:
        pubdate = dt.strptime(pub_date_str, '%Y-%m-%d').replace(hour=0, minute=0, second=0, microsecond=0)
        print('using env.PUB_DATE %s' % pubdate)
    for k, v in item_dict.items():
        feed.add_item(title=k, link=v[0], description=''.join(['<p>{0}</p>'.format(s) for s in v[1].splitlines()]), pubdate=pubdate, unique_id=v[2])
    str_val = feed.writeString('utf-8')
    dom = xml.dom.minidom.parseString(str_val)
    with open('/feeds/end_of_support.xml','w') as fp:
        dom.writexml(fp, encoding='utf-8', newl='\n', indent='', addindent='    ')

    with open(path, 'w') as f:
        json.dump(versions_dict, f, indent=4)

if __name__ == "__main__":
    main()

