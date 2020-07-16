#!/usr/bin/env bash

VERSION=$(sentry-cli releases propose-version || exit)

sed -e "s/(version)/$VERSION/g" < django-test.yaml | kubectl apply -f - || exit
kubectl apply -f nginx-test.yaml || exit

sentry-cli releases --org as207960 deploys $VERSION new -e test
