import re
from operator import xor

import scrapy


class ProxySpider(scrapy.Spider):
    name = 'proxy'
    start_urls = ['http://proxyhttp.net/']

    def parse(self, response):
        script = response.xpath('//*[@id="incontent"]/script[1]').get()
        script_data = re.findall(r'(\w+)\s*=\s*(.+?);', script)

        dict_data = dict()
        for key, value in script_data:
            value = self.get_value(dict_data, value)
            dict_data[key] = value[0] if len(value) == 1 else xor(*value)

        for proxies in response.css('tr')[2:]:
            string_port = proxies.css('td.t_port').get().strip()
            port_raw = re.findall(r'\((.+?)\);', string_port)[0]
            raw = self.get_value(dict_data, port_raw)
            for x in raw[1:]:
                raw[0] ^= x
            yield {
                'ip_address': proxies.css('td.t_ip::text').get().strip(),
                'port': str(raw[0])
            }

    def get_value(self, data, value):
        return [int(x) if x.isdigit() else data[x] for x in value.split('^')]