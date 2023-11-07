import urllib.request as req
from bs4 import BeautifulSoup
import feedgenerator
import xml.dom.minidom

def main():
    url = 'https://docs.contrastsecurity.jp/ja/java-agent-release-notes-and-archive.html'
    res = req.urlopen(url)
    soup = BeautifulSoup(res, 'lxml')
    elems = soup.select('section.section.accordion')
    modified_date = soup.select_one('span.formatted-date').text.strip()

    feed = feedgenerator.Rss201rev2Feed(
        title='Java Agent Release Note',
        link='https://contrastsecurity.dev/contrast-documentation-rss/java_rlsnote.xml',
        description='Java Agent Release Note',
        language='ja',
        pubdate='Tue, 7 Nov 2023 15:20:00 GMT'
    )

    for elem in elems:
        try:
            id_str = elem.get("id")
            title = elem.select('h3.title')[0].text.strip()
            if not title.lower().startswith('java'):
                continue
            desc = elem.select('div.panel-body')[0].text
            url = 'https://docs.contrastsecurity.jp/ja/java-agent-release-notes-and-archive.html#%s' % id_str
            feed.add_item(title=title, link=url, description=desc)
        except IndexError:
            continue

    str_val = feed.writeString('utf-8')
    #print(str_val)
    dom = xml.dom.minidom.parseString(str_val)
    #print(dom.toprettyxml())
    with open('/feeds/java_rlsnote.xml','w') as fp:
        dom.writexml(fp, encoding='utf-8', newl='\n', indent='', addindent='    ')

if __name__ == "__main__":
    main()

