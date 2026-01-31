# Local Run

```bash
docker compose up --build
```

## Verify
### Redis
```bash
docker exec -it $(docker ps -qf name=redis) redis-cli
XRANGE raw:ticks - + COUNT 3
XRANGE clean:ticks - + COUNT 3
```

### Postgres
```bash
docker exec -it $(docker ps -qf name=postgres) psql -U postgres -d nexus
SELECT symbol, ts, price, zscore, is_anomaly FROM ticks_clean ORDER BY ts DESC LIMIT 10;
```
