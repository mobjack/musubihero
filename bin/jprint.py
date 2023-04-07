import sys
import json


def jprint(print_dict, jdent=2, jkeys=True, eexit=True):
    '''Prints the dictionary in pretty json and quits'''

    if not isinstance(print_dict, dict):
        if not isinstance(print_dict, list):
            raise TypeError('jprint requires dict or list')

    if not print_dict:
        raise ValueError('jprint is empty')

    print(json.dumps(print_dict, indent=jdent, sort_keys=jkeys))

    if eexit == True:
        sys.exit()
