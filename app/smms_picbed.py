import requests
import json


class SmmsUpload(object):
    """
    集成sm.ms存储操作
    """
    api_idx='https://sm.ms'

    def __init__(self, token=None):
        if token is None or token=='':
            self.headers={}
        else:
            self.headers={'Authorization':token}

    def upload(self,file_path):
        url=self.api_idx+'/api/v2/upload'
        files={'smfile':file_path}
        r=requests.post(url,files=files,headers=self.headers)
        return json.loads(r.text)

    def delete(self,hash):
        url=self.api_idx+'/api/v2/delete/'+hash
        r=requests.get(url,headers=self.headers)
        return json.loads(r.text)