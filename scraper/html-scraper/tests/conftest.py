from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
#from opentelemetry.exporter.zipkin.proto.http import ZipkinExporter
import opentelemetry.sdk.resources
import opentelemetry.sdk.trace
from opentelemetry.sdk.trace.export import (BatchSpanProcessor,
                                            SimpleSpanProcessor)

otel_resource = opentelemetry.sdk.resources.Resource(attributes={
    opentelemetry.sdk.resources.SERVICE_NAME: "unittest",
})
#zipkin_exporter = ZipkinExporter(endpoint="http://localhost:9411/api/v2/spans")
jaeger_exporter = JaegerExporter()
otel_provider = opentelemetry.sdk.trace.TracerProvider(resource=otel_resource)
otel_processor = BatchSpanProcessor(jaeger_exporter)
#otel_processor = BatchSpanProcessor(jaeger_exporter, max_export_batch_size=24)
#otel_processor = SimpleSpanProcessor(jaeger_exporter)
#otel_processor = SimpleSpanProcessor(zipkin_exporter)
otel_provider.add_span_processor(otel_processor)
trace.set_tracer_provider(otel_provider)
