""" scraper.

scrapes the internet
"""
try:
    from opentelemetry import trace
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    import opentelemetry.sdk.resources
    import opentelemetry.sdk.trace
    from opentelemetry.sdk.trace.export import (BatchSpanProcessor,
                                                SimpleSpanProcessor)

    otel_resource = opentelemetry.sdk.resources.Resource(attributes={
        opentelemetry.sdk.resources.SERVICE_NAME: "unittest",
    })
    otel_provider = opentelemetry.sdk.trace.TracerProvider(
        resource=otel_resource)  #TODO: explictly get AlwaysOnSampler
    otel_exporter = OTLPSpanExporter()
    otel_processor = BatchSpanProcessor(otel_exporter)
    otel_provider.add_span_processor(otel_processor)
    trace.set_tracer_provider(otel_provider)
except ImportError as err:  # pragma: no cover
    import pathlib
    import sys

    sys.path.append(
        str(pathlib.PurePath(__file__).parent.parent / "tests/utils/mock"))

from . import (
    crawler,
    crawler_middleware,
    downloader,
    downloader_middleware,
    perf,
    processor,
    target,
    targets,
    task,
)

Crawler = crawler.Crawler
Downloader = downloader.Downloader
