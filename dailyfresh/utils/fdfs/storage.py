from django.core.files.storage import Storage
from django.conf import settings
from fdfs_client.client import Fdfs_client


class FDFSStorage(Storage):
    # fdfs文件存储类
    '''初始化'''

    def __init__(self, client_conf=None, fdfs_url=None):
        if client_conf is None:
            client_conf = settings.FDFS_CLIENT_CONF
        self.client_conf = client_conf

        if fdfs_url is None:
            fdfs_url = settings.FDFS_URL
        self.fdfs_url = fdfs_url

    def _open(self, name, mode='rb'):
        '''打开文件时'''
        pass

    def _save(self, name, content):
        '''保存文件'''
        # 创建fdfs_client对象
        client = Fdfs_client(self.client_conf)

        # 上传文件
        res = client.upload_by_buffer(content.read())

        # 上传失败
        if res.get('Status') != 'Upload successed.':
            raise Exception('上传失败')

        # 返回所上传文件的id
        return res.get('Remote file_id')

    def exists(self, name):
        '''django判断文件是否可用'''
        return False

    def url(self, name):
        '''返回文件的路径'''
        return self.fdfs_url+name
