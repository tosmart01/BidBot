# -- coding: utf-8 --
# @Time : 2023/5/16 18:15
# @Author : zhuo.wang
# @File : request.py
import json
import time
from typing import Tuple
from abc import ABC, abstractmethod
from datetime import datetime, timedelta

import pandas as pd
import requests
from lxml import etree
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse, unquote
from django.core.cache import cache
from retry import retry
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

import settings
from common.logger import logger
from spider.services.crypto import decrypt
from spider.services.proxy import get_proxy
from spider.services.tools import update_url_params


class BaseProxy(ABC):
    bidType = {'所有类型': 0,
               '公开招标': 1,
               '询价公告': 2,
               '竞争性谈判': 3,
               '单一来源': 4,
               '资格预审': 5,
               '邀请公告': 6,
               '中标公告': 7,
               '更正公告': 8,
               '其他公告': 9,
               '竞争性磋商': 10,
               '成交公告': 11,
               '终止公告': 12}
    bidSort = {'所有类别': 0, '中央公告': 1, '地方公告': 2}
    pinMu = {'所有品目': 0, '货物类': 1, '工程类': 2, '服务类': 3}
    timeType = {'今日': 0, '近3日': 1, '近1周': 2, '近1月': 3, '近3月': 4, '近半年': 5, '近一年': 6, '全部': 7}
    bulletinType = {'全部公告类型': 5, '招标公告': 0, '资格预审公告': 1, '中标候选人公示': 2, '中标结果公示': 3, '更正公告公示': 4}
    page_size = 10

    def get_time_range(self, body, timestamp=True):
        time_type = int(body.get('timeType'))
        current_date = datetime.now().date()
        if body.get('startDate'):
            start_date = pd.to_datetime(body.get('startDate'))
            end_date = pd.to_datetime(body.get('endDate'))
        else:
            if time_type == 0:  # 今日
                start_date = current_date
                end_date = current_date
            elif time_type == 1:  # 近3日
                end_date = current_date
                start_date = end_date - timedelta(days=3)
            elif time_type == 2:  # 近1周
                end_date = current_date
                start_date = end_date - timedelta(days=7)
            elif time_type == 3:  # 近1月
                end_date = current_date
                start_date = end_date - timedelta(days=30)
            elif time_type == 4:  # 近3月
                end_date = current_date
                start_date = end_date - timedelta(days=90)
            elif time_type == 5:  # 近半年
                end_date = current_date
                start_date = end_date - timedelta(days=180)
            elif time_type == 6:  # 近半年
                end_date = current_date
                start_date = end_date - timedelta(days=365)
            elif time_type == 7:
                if timestamp:
                    return None, int(datetime.timestamp(datetime.now()) * 1000)
                else:
                    return '', ''
        if timestamp:
            start_timestamp = int(datetime.combine(start_date, datetime.min.time()).timestamp() * 1000)
            end_timestamp = int(datetime.combine(end_date, datetime.max.time()).timestamp() * 1000)
            return start_timestamp, end_timestamp
        else:
            return start_date.strftime('%Y:%m:%d'), end_date.strftime('%Y:%m:%d')

    @abstractmethod
    def request(self, *args, **kwargs):
        pass

    @abstractmethod
    def parse_html(self, *args, **kwargs):
        pass

    @classmethod
    def merge(self, response_list):
        max_page = max([i[2] for i in response_list if i])
        total = max_page * 40
        rs = []
        for i in response_list:
            if i:
                rs.extend(i[0])
        return rs, total

    def execute(self, body) -> Tuple:
        data = self.request(body)
        response, total = self.parse_html(data)
        max_page = total // self.page_size
        if max_page * self.page_size < total:
            max_page += 1
        return response, total, max_page


class CCGPProxy(BaseProxy):
    page_size = 20
    source = '【来源：中国政府采购网】'

    def request(self, body):
        base_url = '''http://search.ccgp.gov.cn/bxsearch?searchtype=1&page_index=1&bidSort=0&buyerName=&projectId=&pinMu=0&bidType=0&dbselect=bidx&kw=%E6%B1%9F%E8%8B%8F&start_time=2023%3A04%3A15&end_time=2023%3A05%3A16&timeType=3&displayZone=&zoneId=&pppStatus=0&agentName='''
        # 使用urlparse解析URL
        url_parsed = urlparse(base_url)
        # 将查询字符串转换为字典
        url_params = dict(parse_qsl(url_parsed.query))
        isTitleSearch = 1
        if body.get('button') == '内容搜索':
            isTitleSearch = 2
        start_date, end_date = self.get_time_range(body, timestamp=False)
        time_type = body.get('timeType')
        if body.get('startDate'):
            time_type = 6
        update_body = {
            'page_index': int(body.get('page', 1)),
            'kw': body.get('search_text', ''),
            'searchtype': isTitleSearch,
            'displayZone': '上海',
            'timeType': time_type,
            'start_time': start_date,
            'end_time': end_date
        }
        url_params.update(update_body)
        # 创建ChromeOptions对象，并设置无头模式
        chrome_options = Options()
        # chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        # 初始化WebDriver并传入ChromeOptions对象
        driver = webdriver.Chrome(options=chrome_options,executable_path='/usr/local/bin')
        url = update_url_params(base_url, url_params)
        driver.get('http://www.ccgp.gov.cn/')
        driver.delete_all_cookies()
        driver.find_element(value='doSearch1').click()
        driver.delete_all_cookies()
        driver.get(url)
        driver.delete_all_cookies()
        logger.info(f"{self.source} url={url}, page={driver.page_source}")
        driver.find_element(value='inpDisplayZone').click()
        driver.delete_all_cookies()
        element = driver.find_element(by='class name', value='zone_list')
        driver.delete_all_cookies()
        element.find_element(by='xpath', value='//li[text()="上海"]').click()
        html = driver.page_source
        driver.close()
        return html

    def parse_html(self, html) -> Tuple:
        rs = []
        # 创建 lxml 的 HTML 解析器
        parser = etree.HTMLParser()
        # 解析 HTML 字符串
        tree = etree.fromstring(html, parser)
        li_list = tree.xpath("//ul[@class='vT-srch-result-list-bid']/li")
        for li in li_list:
            text = ''.join(li.xpath('span//text()')).split('|')
            for ix, _ in enumerate(text):
                if ix != 0:
                    text[ix] = _.strip().replace('\r\n', '').replace(' ', '')
                else:
                    text[ix] = _.strip().replace('\r\n', '')
            body = {
                'href': ''.join(li.xpath('a/@href')),
                'title': ''.join(li.xpath('a//text()')).strip() + self.source,
                'content': ''.join(li.xpath('p//text()')).strip(),
                'span': text,
            }
            rs.append(body)
        total_str = tree.xpath("//div[@class='vT_z']/div/div/p/span[2]/text()")
        if total_str:
            total = int(total_str[0])
        else:
            total = 0
        logger.info(f"{self.source} 原始数量={total}")
        return rs, total


class ZFCGProxy(BaseProxy):
    page_size = 10
    source = '【来源：上海政府采购网】'

    @retry(tries=3,delay=0.5)
    def request(self, body):
        head = {
            'Content-Type': 'application/json;charset=UTF-8'
        }
        start, end = self.get_time_range(body)
        isTitleSearch = 0
        if body.get('button') == '标题搜索':
            isTitleSearch = 1
        form = {
            "keyword": body.get('search_text', ''),
            "firstCode": body.get('zfcg', ''),
            "secondCode": "",
            "districtCode": [],
            "publishDateBegin": start,
            "publishDateEnd": end,
            "pageNo": int(body.get('page', 1)),
            "pageSize": 10,
            "isTitleSearch": isTitleSearch,
            "order": "desc"
        }
        base_url = '''https://www.zfcg.sh.gov.cn/portal/all'''
        res = requests.post(base_url, headers=head, json=form).json()
        logger.info(f"{self.source}url={base_url},body={form}")
        return res['result']['data']

    def parse_html(self, data):
        rs = []
        base_href = 'https://www.zfcg.sh.gov.cn/luban/detail?categoryCode=%s&articleId=%s&utm=luban.luban-PC-39936.1045-pc-wsg-mainSearchPage-front.16.be345100f46411edba445be08825ba38'
        for row in data['data']:
            publish_time = datetime.fromtimestamp(row.get('publishDate') / 1000)
            body = {
                'title': row.get('title') + self.source,
                'content': row.get('content', '')[:200],
                'href': base_href % (row.get('firstCode'), row.get('articleId')),
                'span': [publish_time.strftime('%F'),row.get('pathName'),row.get('districtName'),row.get('gpCatalogName'),]
            }
            rs.append(body)
        logger.info(f"{self.source} 原始数量={data['total']}")
        return rs, data['total']

    @classmethod
    def zfcg_select(self, ):
        select = cache.get('select')
        if not select:
            select = requests.get(settings.ZFCG_SELECT_URL + str(int(time.time()))).json()['result']['json']
            cache.set('select', select, 3600 * 24)
        return select


class ctbpspProxy(BaseProxy):
    page_size = 10
    source = '【来源：全国招标公告公式搜索引擎】'

    @retry(tries=3,delay=0.5)
    def request(self, body):
        """
        keyword: 上海国际招标有限公司
        uid: 0
        PageSize: 10
        CurrentPage: 1
        searchType: 0
        bulletinType: 5
        :param body:
        :return:
        """
        base_url = 'https://custominfo.cebpubservice.com/cutominfoapi/searchkeyword'
        # 使用urlparse解析URL
        url_parsed = urlparse(base_url)
        # 将查询字符串转换为字典
        url_params = dict(parse_qsl(url_parsed.query))
        search_text = '上海'
        if '上海' not in body.get('search_text'):
            search_text = f"{body.get('search_text')}{search_text}"
        if '上海' in body.get('search_text'):
            search_text = body.get('search_text')

        update_body = {
            'uid': 0,
            'PageSize': 10,
            'CurrentPage': int(body.get('page', 1)),
            'searchType': 0,
            'bulletinType': body.get('bulletinType',5),
            'keyword': search_text,
        }
        url_params.update(update_body)
        response = requests.get(base_url, params=url_params, proxies=get_proxy())
        logger.info(f"{self.source} url = {unquote(response.url)}")
        response.input_value = search_text
        return response


    def parse_html(self, response):
        if response.status_code == 200:
            rs = []
            encode_text = response.text[1:-1]
            response_data = json.loads(decrypt(encode_text))
            data = response_data['data']['dataList']
            total_count = response_data['data']['totalCount']
            link = 'http://ctbpsp.com/#/bulletinDetail?uuid=%s&inpvalue=%s&dataSource=%s'
            for row in data:
                body = {
                    'title': row.get('noticeName') + self.source,
                    'content': '',
                    'href': link%(row.get('bulletinID'),response.input_value,row.get('dataSource')),
                    'span': [row.get('reginProvince'),row.get('bulletinTypeName'),row.get('noticeSendTime'),],
                }
                rs.append(body)
            logger.info(f"{self.source} 原始数量={total_count}")
            return rs, total_count
        return [], 0


class SpiderProxy(BaseProxy):
    engine_map = {
        ctbpspProxy.__name__: ctbpspProxy,
        ZFCGProxy.__name__: ZFCGProxy,
        CCGPProxy.__name__: CCGPProxy
    }
    def __init__(self, name):
        self.engine = self.engine_map.get(name)()

    @classmethod
    def run(self,name, body) -> Tuple:
        return self.engine_map.get(name)().execute(body)


