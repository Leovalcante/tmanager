#!/usr/bin/env bash
#
# This is the pre-commit.bash that will be git pre-commit hook

echo "Running pre-commit hook"

# Running tests
./hooks/run-test.bash

# $? stores exit value of the last command
# If a test fail $? will be != 0
if [[ $? -ne 0 ]]; then
 echo "Tests must pass before commit!"
 exit 1
fi