name: Eagle Runner

on:
  push:
    paths:
      - "eagle/jobs/*.json"
  workflow_dispatch: {}

jobs:
  run-eagle:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout Repo
        uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.10"

      - name: Install Dependencies
        run: |
          pip install pydantic

      - name: Run Eagle
        run: |
          python run_eagle.py
          
      - name: Commit Outputs
        run: |
          git config --global user.name "Keeper"
          git config --global user.email "keeper@example.com"
          git add eagle/output/*
          git commit -m "Eagle Output - $(date)" || echo "No changes"
          git push
