#!/bin/bash
echo "Access local instance on http://localhost:5000"
docker run --rm -t -i \
	-v ./instance:/vds/instance \
	-v ./config.json:/vds/config.json:ro \
	-p 5000:5000 \
	-e TRUSTED_PROXY="127.0.0.1" \
	-e TRUSTED_PROXY_HEADERS="forwarded" \
	penglmaier/vds-sternwarte
