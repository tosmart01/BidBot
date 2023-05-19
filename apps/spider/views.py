from concurrent.futures import ThreadPoolExecutor, as_completed

from retry import retry
from django.http import JsonResponse
from django.shortcuts import render

from django.views import View

from spider.services.request import SpiderProxy, ZFCGProxy, CCGPProxy, ctbpspProxy
from common.logger import logger


class Search(View):
    pool = ThreadPoolExecutor(max_workers=10)

    def get(self, request):
        select = ZFCGProxy.zfcg_select()
        context = {
            'bidType': SpiderProxy.bidType,
            'bidSort': SpiderProxy.bidSort,
            'pinMu': SpiderProxy.pinMu,
            'timeType': SpiderProxy.timeType,
            'zfcg_name': {i['name']: i['id'] for i in select},
            'bulletinType': SpiderProxy.bulletinType,
        }
        return render(request, 'search.html', context)

    def async_request(self, name, body):
        try:
            return SpiderProxy.run(name, body)
        except Exception:
            logger.exception(f"{name}任务失败")
            return []

    def post(self, request):
        page = int(request.POST.get('page',1))
        body = request.POST.copy()
        jobs = []
        for name in [CCGPProxy.__name__,ZFCGProxy.__name__, ctbpspProxy.__name__]:
            jobs.append(self.pool.submit(self.async_request, name, body))
        response_list = []
        for job in as_completed(jobs):
            response_list.append(job.result())
        response, total = SpiderProxy.merge(response_list)
        return JsonResponse({'total_items': total, 'results': response, 'current_page': page}, safe=False)