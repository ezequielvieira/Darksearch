#!/usr/bin/python

import sys
sys.path.append('C:/Users/Ezequiel Vieira/Darksearch/darksearch')

from darksearch.darkmain import app as application

def main():
    application.run(
            host='0.0.0.0',
            port=80,
            threaded=True,
            debug=True
    )

if __name__ == '__main__':
    main()
