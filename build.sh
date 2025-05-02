#!/usr/bin/env bash

# Install Poetry
pip install poetry

# Configure Poetry to not use virtual environments
poetry config virtualenvs.create false

# Install dependencies
poetry install --no-interaction --no-ansi
