#! /usr/bin/env python3

import re
import urllib.request
import time
import webbrowser
import time
import lxml.html


class Watchdog:
    '''
    Watchdog for AmebaBlog
    Parameter Watchdog(blog_URL, date, action, interval=10)
    - blog_URL: watching target url
    - action: do action when update new entry
    - date: watching point (format: %Y-%m-%d %H:%M:%S)
    - interval: access interval sec (more than 1sec)
    '''

    re_entry = re.compile('entry-.+?+.html')
    re_date = re.compile('\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}')

    def __init__(self, url, action,
                 interval=60, date=time.strftime('%Y-%m-%d %H:%M:%S')):
        self.url = url.rstrip('/') + '/'
        self.date = date
        self.action = action
        self.interval = interval

    def get_entry(self, html):
        return sorted(re.findall(self.re_entry, html))[-1]

    def get_date(self, html):
        return sorted(re.findall(self.re_date, html))[-1]

    def get_title(self, html):
        return [lxml.html.fromstring(h1).text_content().strip()
                for h1 in re.findall('<h1.*?</h1>', html, flags=re.DOTALL)]

    def get_info(self, html):
        return {
            'new_entry': self.get_entry(html),
            'date': self.get_date(html),
            'title': '/'.join(self.get_title(html)),
        }


    def run(self):
        while True:
            res = urllib.request.urlopen(self.url)
            html = res.read().decode('utf-8')
            info = self.get_info(html)

            if info['date'] > self.date:
                self.date = info['date']
                info.update({'url': self.url + info['new_entry']})
                self.action(info)
            time.sleep(self.interval)


def browser(info):
    webbrowser.open(info['url'])
    print(info)


if __name__ == '__main__':
    rihochan_watchdog = Watchdog('http://ameblo.jp/yoshi-rihorihoriho/',
                                 browser,
                                 date='2015-05-31 00:00:00',
    )
    rihochan_watchdog.run()
