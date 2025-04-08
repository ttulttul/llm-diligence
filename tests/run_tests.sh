#!/bin/bash

# Run all tests with coverage report
pytest -xvs --cov=models --cov=analysis --cov=utils tests/
