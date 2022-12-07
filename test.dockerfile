# syntax=docker/dockerfile:1
FROM python:3.10

# COPY --link raw-input-data .

WORKDIR /app
ENV CODEBASE=scraper/html-scraper
COPY --link $CODEBASE/pyproject.toml .
RUN pip install --no-cache-dir -e ".[tests]"

COPY $CODEBASE/scraper scraper
RUN pip install --no-cache-dir -e .
# RUN ln -sf ../raw-input-data scraper/targets
COPY $CODEBASE/tests tests

# VOLUME /results
CMD [ "pytest" ]