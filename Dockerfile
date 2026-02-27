FROM apache/airflow:2.8.1

# Switch to root only to install system deps (psql client for init.sql)
USER root
RUN apt-get update \
 && apt-get install -y --no-install-recommends postgresql-client \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# Copy entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Pre-create log/data directories with correct ownership so they are
# never created as root by Docker volume mounts.
# AIRFLOW_UID defaults to 50000 (airflow image default).
ARG AIRFLOW_UID=50000
RUN mkdir -p /opt/airflow/logs /opt/airflow/data \
 && chown -R ${AIRFLOW_UID}:0 /opt/airflow/logs /opt/airflow/data \
 && chmod -R 775 /opt/airflow/logs /opt/airflow/data

# Drop back to the airflow user
USER ${AIRFLOW_UID}

# Copy optional init SQL (runs once on first boot)
COPY --chown=${AIRFLOW_UID}:0 init.sql /opt/airflow/init.sql

ENTRYPOINT ["/entrypoint.sh"]
# Default command – overridden per-service in docker-compose.yml
CMD ["webserver"]
