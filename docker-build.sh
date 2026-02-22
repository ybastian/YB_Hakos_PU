#!/bin/bash
# specify options if needed
echo docker build -t vds-sternwarte:latest . $@
docker build -t vds-sternwarte:latest . $@
echo docker tag vds-sternwarte:latest penglmaier/vds-sternwarte:latest
docker tag vds-sternwarte:latest penglmaier/vds-sternwarte:latest
