
import os

# one art config
ONE_ART_SECRET = os.getenv('ONE_KEY', 'FLVQt0kKf+wAwV0D8rSOXg==').encode('utf8')
ONE_ART_AUTH = os.getenv('ONE_AUTH', 'eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiIxNzMxNzUzMzE0NiIsImlhdCI6MTY1ODEzNjEwMCwiZXhwIjoxNjU4NzQwOTAwfQ._Y36A0-xmtGt4Y2Um_AZ31vur9fUmOpNaB_YL5XLPGvO6lBaLxS0hThKkUAcI9-FMgH2bhcxykcCWtBr3jBJ3A')
ONE_ART_SIG = os.getenv('ONE_SIG', 'ZinduNDMDR76WKqMoFGE9fEjKUH0Kq0wrVH5P4+1nqefDuJuJjc+8XRxkxClk8Zue0DFSKtDttgXIXdDhuWLIQ==')

# bmark config
BMARK_AUTH = os.getenv('BMARK_AUTH', 'dcf82b3a-47f5-460d-a127-f2ff129e49c0')

# xumi config
TAOBAO_TOKEN = os.getenv('TB_AUTH',
                         'cna=q+YxGVWaeSECATr2Aa52/0y9; cookie2=1d3d0865a9b12749bbece6a4828fe6a1; t=69404c75a7f64d5177a15984555d5960; _tb_token_=f16ee3379ee75; linezing_session=9jsBg6p00z4G6ZM37lGaLvcr_1655442903927FyFu_1; xlly_s=1; _m_h5_tk=7e6bd2384377b1d51bffd9596e9dfa8a_1656502966408; _m_h5_tk_enc=1fe0cb90bbe05b9fd4262118ee84e0bb; uc1=cookie14=UoexND%2FU5KPBGA%3D%3D; l=eBOe46F4LnKbDmjWBO5CFurza77TqIRb4sPzaNbMiInca6sFT3m21NChJGUM7dtjgtCXTeKzDkQvwdLHRH-gQMo4Y_w4f2YS3xvO.; tfstk=cHsfBJOgapArOJUZ0twzu9KLKEtGZlkBCrOch7CrrlOg-3WfiRmeOdJOSfKwBL1..; isg=BJmZsGEgH7TzPMM2sWxBCO-gqIxzJo3YahYu37tO3kBswrlUAne8qlncxIa0-iUQ')

MAX_RETRY = int(os.getenv('RETRY', 5))
ENABLE_DING = os.getenv('ENABLE_DING')
ENABLE_PROXY = os.getenv('ENABLE_PROXY')
DING_ADDRESS = os.getenv('DING', 'https://oapi.dingtalk.com/robot/send?access_token=01a408d403e41d7d9dd9008670e1a1b71493ac3125f13f9c3cd6cc437c9fcfab')


def parse_mysql_config(url):
    url = url[url.index('://') + 3:]
    username, password = url[:url.index('@')].split(':')
    url = url[url.index('@') + 1:]
    db = url[url.index('/') + 1:]
    host, port = url[:url.index('/')].split(":")
    return {
        'host': host,
        'port': int(port),
        'user': username,
        'password': password,
        'db': db
    }


MYSQL_CONFIG = parse_mysql_config(
    os.getenv('MYSQL', 'mysql://root:wealthnov11d@r2.dsjcj.cc:10196/digital_collection_spider'))

MYSQL_DATA_CONFIG = parse_mysql_config(
    os.getenv('MYSQL_DATA', 'mysql://root:wealthnov11d@r2.dsjcj.cc:10196/digital_collection_data'))

