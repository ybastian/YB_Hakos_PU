#!/bin/bash
# specify options if needed
docker build -t vds-sternwarte:latest . $@
docker tag vds-sternwarte:latest penglmaier/vds-sternwarte:latest
