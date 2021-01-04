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

CREATE table storage.sensors_all as storage.sensors_data
Engine = Distributed(awesome_cluster, storage, sensors_data, rand());


CREATE MATERIALIZED VIEW IF NOT EXISTS storage.minute_lens
ENGINE = AggregatingMergeTree()
ORDER BY timeslice POPULATE AS
SELECT
  toUInt64(FLOOR(timestamp/60)*60) AS timeslice, avgState(data) as aggregate
FROM storage.sensors_data
GROUP BY timeslice;
-- TODO: maybe also group by id

create table storage.distr_minute_lens AS storage.minute_lens
ENGINE = Distributed(awesome_cluster, storage, minute_lens);
