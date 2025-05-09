#!/bin/bash
echo "Running Flake8..."
flake8 "$(dirname "$0")/.."