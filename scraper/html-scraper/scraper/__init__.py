""" scraper.

scrapes the internet
"""
try:  # pragma: no cover
    from opentelemetry import trace
    if (use_grpc_instead_of_thrift := 0):
        from opentelemetry.exporter.jaeger.proto.grpc import JaegerExporter
    else:
        from opentelemetry.exporter.jaeger.thrift import JaegerExporter
    import opentelemetry.sdk.resources
    import opentelemetry.sdk.trace
    from opentelemetry.sdk.trace.export import (BatchSpanProcessor,
                                                SimpleSpanProcessor)

    otel_resource = opentelemetry.sdk.resources.Resource(attributes={
        opentelemetry.sdk.resources.SERVICE_NAME: "unittest",
    })
    if use_grpc_instead_of_thrift:
        jaeger_exporter = JaegerExporter(collector_endpoint="localhost:14250",
                                         insecure=True)
    else:
        jaeger_exporter = JaegerExporter()
    otel_provider = opentelemetry.sdk.trace.TracerProvider(
        resource=otel_resource)  #TODO: explictly get AlwaysOnSampler
    otel_processor = BatchSpanProcessor(jaeger_exporter)
    # NOTE: use "OTEL_BSP_MAX_EXPORT_BATCH_SIZE=24 pytest" on macOS, or add "max_export_batch_size=24" to BatchSpanProcessor options, or alter MTU
    #otel_processor = SimpleSpanProcessor(jaeger_exporter)
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
