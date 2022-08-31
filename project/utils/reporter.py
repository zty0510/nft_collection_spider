
import requests

from project.config import DING_ADDRESS, ENABLE_DING


def ding_report(content, at_mobiles=None):
    if not DING_ADDRESS or not ENABLE_DING:
        print(content)
        return
    if not at_mobiles:
        at_mobiles = []
    return requests.post(DING_ADDRESS, json={'msgtype': 'text', 'text': {'content': '数藏告警\n' + content},
                                             'at': {'atMobiles': [str(m) for m in at_mobiles]}}).json()


if __name__ == '__main__':
    print(ding_report('test'))

