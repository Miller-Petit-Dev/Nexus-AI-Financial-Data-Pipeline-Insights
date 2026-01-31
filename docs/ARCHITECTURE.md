# Architecture (Clean Architecture)

## Layers
- **Domain**: canonical models + ports (interfaces)
- **Application**: use-cases (ingestion, processing)
- **Infrastructure**: Redis/Postgres/NLP implementations
- **Apps**: runtime entrypoints (ingestor, processor, mock_ws)

## Data Flow
WebSocket -> Ingestor (Pydantic validate) -> Redis Stream `raw:ticks`
`raw:ticks` -> Processor (consumer group) -> Anomaly filter -> Postgres (`ticks_clean`) -> Redis Stream `clean:ticks`

## Scaling
- Run multiple `processor` replicas with different `TICKS_CONSUMER` values under the same consumer group.
- Redis Streams will distribute messages across consumers in the group.

