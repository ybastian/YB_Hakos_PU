#!/bin/sh
python --version
flask db upgrade
cat prod.py
exec python prod.py
