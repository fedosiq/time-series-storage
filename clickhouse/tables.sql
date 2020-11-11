CREATE database storage;

CREATE TABLE IF NOT EXISTS storage.queue (
    id UInt32,
    timestamp UInt64,
    data Float64
  ) ENGINE = Kafka('kafka-1:19093,kafka-2:19093', 'telemetry', 'telemetry-group')
              SETTINGS kafka_format = 'JSONEachRow',
                       kafka_num_consumers = 1;

CREATE TABLE IF NOT EXISTS storage.sensors_data (
    id UInt32,
    timestamp UInt64,
    data Float64
) ENGINE = MergeTree()
ORDER BY timestamp;

CREATE MATERIALIZED VIEW IF NOT EXISTS storage.queue_mv TO storage.sensors_data
  AS SELECT * FROM storage.queue;
