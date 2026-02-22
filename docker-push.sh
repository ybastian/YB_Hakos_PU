#!/bin/bash
echo docker push penglmaier/vds-sternwarte:latest
docker push penglmaier/vds-sternwarte:latest
if [ -n "$1" ]; then
  echo docker tag penglmaier/vds-sternwarte penglmaier/vds-sternwarte:$1
  docker tag penglmaier/vds-sternwarte penglmaier/vds-sternwarte:$1
  echo docker push penglmaier/vds-sternwarte:$1
  docker push penglmaier/vds-sternwarte:$1
fi
