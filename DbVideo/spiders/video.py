# -*- coding: utf-8 -*-
import scrapy
import json
import re
from DbVideo import settings

class VideoSpider(scrapy.Spider):
    name = 'video'
    allowed_domains = ['douban.com']
    base_url = 'https://movie.douban.com/j/new_search_subjects?sort=U&range=0,10&tags=%E7%94%B5%E5%BD%B1&start={}'
    start_urls = ['https://movie.douban.com/j/new_search_subjects?sort=U&range=0,10&tags=%E7%94%B5%E5%BD%B1&start=0']
    cookies_str = settings.COOKIE_STR
    cookies = {i.split('=')[0]:i.split('=')[1] for i in cookies_str.split(';')}
    num = 0
    def start_requests(self):
        yield scrapy.Request(
            self.base_url.format(self.num*20),
            cookies=self.cookies,
            callback=self.parse
        )

    def parse(self, response):
        json_data = response.text
        data = json.loads(json_data)
        for v in data['data']:
            item = {}
            item['directors'] = v['directors']
            item['title'] = v['title']
            item['id'] = v['id']
            item['rate'] = v['rate']
            item['casts'] = v['casts']
            detail_url = v['url']

            yield scrapy.Request(
                detail_url,
                callback=self.parse_detail,
                meta={'item':item}
            )
        self.num += 1
        yield scrapy.Request(
            self.base_url.format(self.num*20),
            callback=self.parse
        )

    def parse_detail(self,response):
        item = response.meta['item']
        item['type'] = response.xpath("//span[@property='v:genre']//text()").extract()
        item['country'] = re.findall('<span class="pl">制片国家/地区:</span> (.*?)<br/>',response.text)
        item['runtime'] = response.xpath("//span[@property='v:runtime']/@content").extract_first()
        item['date'] = response.xpath("//span[@property='v:initialReleaseDate']//@content").extract()
        item['contents'] = response.xpath("//span[@property='v:votes']/text()").extract_first()
        yield item