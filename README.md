
## Docker Setup and Data Ingestion

### 1. Stop the other PostgreSQL container to avoid port conflict

```bash
docker stop pg_test
```

### 2. Start PostgreSQL and pgAdmin using Docker Compose

```bash
docker compose up -d
```

### 3. Check running containers

```bash
docker compose ps
```

### 4. Connect PostgreSQL container to the project network

```bash
docker inspect dataengineeringproject-pgdatabase-1 \
  --format '{{json .NetworkSettings.Networks}}' \
  | grep -q 'dataengineeringproject_default' \
  || docker network connect --alias pgdatabase \
  dataengineeringproject_default \
  dataengineeringproject-pgdatabase-1
```

### 5. Test PostgreSQL hostname resolution

```bash
docker run --rm \
  --network=dataengineeringproject_default \
  postgres:18 \
  getent hosts pgdatabase
```

### 6. Build the ingestion Docker image

```bash
docker build -t chicago_crimes_ingest:v001 .
```

### 7. Run the ingestion container

```bash
docker run -it --rm \
  --network=dataengineeringproject_default \
  chicago_crimes_ingest:v001 \
  --pg-host=pgdatabase \
  --target-table=chicago_crimes
```
