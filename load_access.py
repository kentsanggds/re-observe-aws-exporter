"""
Prints outs the user provided credentials to be exported as environment variables
"""

import os
import json


if __name__ == '__main__':
    vcap_services = json.loads(os.environ['VCAP_SERVICES'])
    user_provided = vcap_services['user-provided']

    for key in user_provided[0]['credentials']:
        print("{}={}".format(key, user_provided[0]['credentials'][key]))
