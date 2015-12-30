
import os
import sys
import json
import time

from iddt.dispatcher import Dispatcher

import logging

logging.basicConfig(filename='iddt.cli.log', level=logging.DEBUG)
logger = logging.getLogger('iddt.cli')


class CLIDispatcher(Dispatcher):

    def __init__(self):
        super(CLIDispatcher, self).__init__()


if __name__ == '__main__':

    if len(sys.argv) != 4:
        print(
            ('Usage:\n\n\tpython cli.py <target_url> ',
             '<link_level> <allowed_domains_json_list>\n')
        )
    else:
        try:
            target_url = sys.argv[1]
            link_level = int(float(sys.argv[2]))
            allowed_domains = json.loads(sys.argv[3])

            d = CLIDispatcher()
            d.dispatch(
                {
                    'target_url': target_url,
                    'link_level': link_level,
                    'allowed_domains': allowed_domains,
                },
                clean_job=False,
            )
            print(json.dumps(d.get_documents(), indent=4))
        except:
            print('Invalid inputs.  Please check the inputs and try again.')
    print('iddt: done')
