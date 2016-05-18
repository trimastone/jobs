#!/bin/bash -ex
python mk_template.py $2 $3
s3cmd put servers.json s3://trimastone/servers.json --server-side-encryption
aws cloudformation create-stack --stack-name $1 --template-url https://s3.amazonaws.com/trimastone/servers.json
