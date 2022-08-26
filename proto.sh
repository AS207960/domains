#!/usr/bin/env bash

python3 -m grpc_tools.protoc --python_out=domains/epp_api/epp_grpc/ --grpc_python_out=domains/epp_api/epp_grpc/ -I ../epp-proxy/proto/  ../epp-proxy/proto/**/*.proto

find domains/epp_api/epp_grpc -mindepth 2 -name \*.py -exec bash -c "FILE={}; sed -E \"/^from (google\.)|(\.\.)/! s/^from (.+)/from \.\.\1/\" \$FILE > \$FILE.new; mv \$FILE.new \$FILE" \;
find domains/epp_api/epp_grpc -maxdepth 1 -name \*.py -exec bash -c "FILE={}; sed -E \"/^from (google\.)|(\.)/! s/^from (.+)/from \.\1/\" \$FILE > \$FILE.new; mv \$FILE.new \$FILE" \;
find domains/epp_api/epp_grpc -maxdepth 1 -name \*.py -exec bash -c "FILE={}; sed -E \"/^from (google\.)|(\.)/! s/^import (.+_pb2)/from \. import \1/\" \$FILE > \$FILE.new; mv \$FILE.new \$FILE" \;
