#!/bin/bash

flake8 --exclude=".venv,./stacktach/migrations,./stacktach/settings.py" \
    --ignore="E121,E122,E123,E124,E126,E127,E128,E711,E712,H102,H404,F403,F811,F841,H803" \
    .
