""" scraper.

scrapes the internet
"""
from . import (crawler, crawler_middleware, downloader, downloader_middleware,
               perf, target, targets, task)

Crawler = crawler.Crawler
Downloader = downloader.Downloader
