"""
Auto teacher evaluation placeholder.
To be implemented: fetch evaluation table and submit default evaluations.
"""

from staticINF import *

import requests
import hashlib
import ddddocr
import json

def teacherEvaluate(_http_main):
    """
    Placeholder for automated teacher evaluation.
    Should fetch evaluation table and submit default evaluations.
    :param _http_main: authenticated session.
    """
    res = _http_main.get(evaluationTable_url, headers=http_head)
    table = json.loads(res)
