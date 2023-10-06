
import sys
import json
import uuid
import traceback
import pendulum
import jsonlines
from jprint import jprint
from shortuuid import ShortUUID as uuid


msg_keys = set(['loglevel', 'name', 'info'])
logfile = '../logs/musubi-log.jsonl'


def logit(log_dict):
    if not isinstance(log_dict, dict):
        raise TypeError('Log message is not a dictionary')

    if not msg_keys.issubset(log_dict.keys()):
        raise KeyError(
            'check logit required keys: loglevel, name, info')

    log_dict['eid'] = uuid().random(length=12)
    #log_dict['ts'] = int(pendulum.now().format('X'))
    log_dict['ts'] = pendulum.now().to_iso8601_string()

    with jsonlines.open(logfile, 'a') as lf:
        lf.write(log_dict)


def my_exception_hook(type, value, tb):
    traceback_details = '\n'.join(traceback.extract_tb(tb).format())
    except_msg = {'loglevel': 'error',
                  'name': 'caught exception',
                  'info': {
                      'except_type': type,
                      'except_value': value,
                      'traceback': traceback_details
                  }
                  }
    logit(except_msg)
