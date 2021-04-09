from qiniu import Auth, put_file, etag
import qiniu.config

access_key = 'ix9ufMXmeNyU7Hm71D13DlYHGRH1sm-esKX7vUkX'
secret_key = 'C2Y8-U_SA3yBDQtEhGGNZiS4ylT_3hpb2ZOSMeNd'

q = Auth(access_key, secret_key)
bucket_name = 'rideshare'


def uploadFileTo(_key,_path):
    key = _key
    # 生成上传 Token，可以指定过期时间等
    token = q.upload_token(bucket_name, key, 3600)

    # 要上传文件的本地路径
    localfile = _path
    ret, info = put_file(token, key, localfile)
    print(info)

    assert ret['key'] == key
    assert ret['hash'] == etag(localfile)

if __name__ == "__main__":
    uploadFileTo("route.json","Visualization/orders/json/routes.json")

