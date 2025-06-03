from staticINF import *

import requests
import hashlib
import ddddocr
import json

def teacherEvaluate(_http_main):
    res = _http_main.get(evaluationTable_url, headers=http_head)
    table = json.loads(res)
