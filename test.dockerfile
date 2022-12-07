# syntax=docker/dockerfile:1
FROM python:3.10

WORKDIR /app
ENV CODEBASE=scraper/html-scraper

# install app dependencies
COPY --link $CODEBASE/pyproject.toml .
RUN pip install --no-cache-dir -e ".[tests]"

# install app
COPY $CODEBASE/scraper scraper
RUN pip install --no-cache-dir -e .

# install tests
COPY --link raw-input-data scraper/targets
COPY $CODEBASE/tests tests

# VOLUME /results
CMD [ "pytest" ]
