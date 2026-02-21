#!/bin/bash
docker push penglmaier/vds-sternwarte:latest
if [ -n "$1" ]; then
  docker tag penglmaier/vds-sternwarte penglmaier/vds-sternwarte:$1
  docker push penglmaier/vds-sternwarte:$1
fi
