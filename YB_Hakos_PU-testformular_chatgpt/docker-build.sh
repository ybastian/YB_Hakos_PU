#!/bin/bash
docker build -t vds-sternwarte:latest .
docker tag vds-sternwarte:latest penglmaier/vds-sternwarte:latest
