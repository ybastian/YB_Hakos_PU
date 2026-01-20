#!/usr/bin/env python
import sys
if sys.version_info.major < 3:
    print("Cannot run with python 2")
    exit(1)
if sys.version_info.minor != 12:
    print("WARNING: -------------------------------------------")
    print("WARNING: not running with recommended python version")
    print("WARNING: -------------------------------------------")

from webapp import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
