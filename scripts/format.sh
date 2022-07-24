#!/bin/sh -e
set -x
isort --recursive --force-single-line-imports --apply asyncbbb
autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place asyncbbb
black asyncbbb
isort --recursive --apply asyncbbb