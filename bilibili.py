import requests
import json
import traceback
import pymongo


def exception_capture(func):
    """
    装饰器
    :param func: 函数对象
    :return:
    """

    def work(*args, **kwargs):
        """
        捕捉异常并写入文件
        :param args: 位置参数
        :param kwargs: 关键字参数
        :return:
        """
        file = open("log.log", 'a', encoding='utf-8')
        try:
            func(*args, **kwargs)  
        except Exception as e:
            traceback.print_exc(limit=None, file=file)  
        file.close()

    return work


class Bilibili(object):
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/84.0.4147.89 Safari/537.36",
        'Referer': "https://search.bilibili.com"
        }

    file = open("log.log", 'a', encoding='utf-8')

    def __init__(self, keyword: str):
        self.keyword = keyword  
        self._numPages = 0
        self.get_official_works()

    @exception_capture
    def get_official_works(self):
        s = 0
        client = pymongo.MongoClient('localhost',27017)
        db = client.bilibili
        collenction = db.video
        for x in collenction.find({'title':{"$regex": self.keyword}}):
            if x:
                print(x)
            else:
                for i in range(1,51):
                    url = "https://api.bilibili.com/x/web-interface/search/all/v2?context=&page="+str(i)+"&order=&keyword={" \
                        "}&duration=&tids_1=&tids_2=&__refresh__=true&_extra=&highlight=1&single_column=0&jsonp=jsonp&callback" \
                        "=__jp0"
                    response = requests.get(url=url.format(self.keyword), headers=self.headers).text  
                    #print(response)
                    data = json.loads(response[6:len(response) - 1])  
                    #print(data)
                    self._numPages = data['data']['numPages']
                    for data_result in data['data']['result']:
                        if data_result['data']:
                            for data_result_url in data_result['data']:
                                if data_result_url['type']=='video':
                                    #print(data_result_url)
                                    json_video ={
                                        'id':data_result_url['id'],
                                        'url':data_result_url['arcurl'],
                                        'title':data_result_url['title'],
                                        'description': data_result_url['description'],
                                        'tag':data_result_url['tag'],
                                        'review':data_result_url['review'],
                                        'like':data_result_url['like'],
                                        'duration':data_result_url['duration']
                                        }
                                    res = collenction.count_documents({'url':data_result_url['id']})
                                    if res ==0:
                                        s = s+1
                                        myquery = {'id':data_result_url['id']}
                                        collenction.update(myquery,json_video,upsert=True)
                                        #print(json_video)
                for x in collenction.find({'title':{"$regex": self.keyword}}):
                    print(x)

        







       
                            
        


search = input('请输入需要查询的课程：')
a = Bilibili(search)
