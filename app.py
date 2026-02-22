#!/usr/bin/env python
import sys

py_version=f"{sys.version_info.major}.{sys.version_info.minor}"
print(f"Python Version: {py_version}.{sys.version_info.micro}")

if sys.version_info.major < 3:
    print("Cannot run with python 2")
    exit(1)

py_version_recommended="3.14"
if py_version != py_version_recommended:
    print("WARNING: ------------------------------------------------")
    print(f"WARNING: not running with recommended python version {py_version_recommended}")
    print("WARNING: ------------------------------------------------")


from webapp import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
