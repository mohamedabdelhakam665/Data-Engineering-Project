# 1. Stop the other PostgreSQL container to avoid port conflict
docker stop pg_test

# 2. Start PostgreSQL and pgAdmin using Docker Compose
docker compose up -d

# 3. Check running containers
docker compose ps

# 4. Connect PostgreSQL container to the project network
# Only connect if it is not already connected
docker inspect dataengineeringproject-pgdatabase-1 \
  --format '{{json .NetworkSettings.Networks}}' \
  | grep -q 'dataengineeringproject_default' \
  || docker network connect --alias pgdatabase \
  dataengineeringproject_default \
  dataengineeringproject-pgdatabase-1

# 5. Test PostgreSQL hostname resolution
docker run --rm \
  --network=dataengineeringproject_default \
  postgres:18 \
  getent hosts pgdatabase

# 6. Build the ingestion Docker image
docker build -t chicago_crimes_ingest:v001 .

# 7. Run the ingestion container
docker run -it --rm \
  --network=dataengineeringproject_default \
  chicago_crimes_ingest:v001 \
  --pg-host=pgdatabase \
  --target-table=chicago_crimes