#!/bin/bash

# Install required test packages
pip install -r tests/requirements-test.txt

# Run all tests with coverage report
pytest -xvs --cov=models --cov=analysis --cov=utils tests/
