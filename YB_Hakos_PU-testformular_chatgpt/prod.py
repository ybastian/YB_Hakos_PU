#!/usr/bin/env python

from webapp import create_app
import os

print("STARTING PRODUCTION SERVER")

app = create_app()

from waitress import serve
from paste.translogger import TransLogger
# see: https://docs.pylonsproject.org/projects/waitress/en/stable/arguments.html
serve(TransLogger(app, setup_console_handler=(os.getenv('SETUP_CONSOLE_HANDLER', 'false').lower() in ('true', '1', 't'))),
    listen=os.getenv('LISTEN', '0.0.0.0:5000'),
    url_scheme=os.getenv('URL_SCHEMA', 'https'),
    threads=int(os.getenv('THREADS','4')),
    trusted_proxy_count=int(os.getenv('TRUSTED_PROXY_COUNT', '1')),
    trusted_proxy=os.getenv('TRUSTED_PROXY', '172.22.0.6'),
    trusted_proxy_headers=os.getenv('TRUSTED_PROXY_HEADERS', 'x-forwarded-for x-forwarded-host x-forwarded-proto x-forwarded-port'),
    log_untrusted_proxy_headers=(os.getenv('LOG_UNTRUSTED_PROXY_HEADERS', 'true').lower() in ('true', '1', 't'))
    )
