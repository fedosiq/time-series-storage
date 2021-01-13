CREATE database storage;

CREATE TABLE IF NOT EXISTS storage.queue (
    id UInt32,
    timestamp UInt64,
    data Float64
  ) ENGINE = Kafka()
SETTINGS
    kafka_broker_list = 'kafka-1:19093',
    kafka_topic_list = 'telemetry',
    kafka_group_name = 'telemetry-group',
    kafka_format = 'JSONEachRow';

CREATE TABLE IF NOT EXISTS storage.sensors_data (
    id UInt32,
    timestamp UInt64,
    data Float64
) ENGINE = ReplacingMergeTree()
ORDER BY (timestamp, id, data); -- in ReplacingMergeTree uniqueness is defined by order by key

CREATE MATERIALIZED VIEW IF NOT EXISTS storage.queue_mv TO storage.sensors_data
  AS SELECT * FROM storage.queue;

CREATE table storage.sensors_all as storage.sensors_data
Engine = Distributed(awesome_cluster, storage, sensors_data, rand());


CREATE MATERIALIZED VIEW IF NOT EXISTS storage.minute_lens
ENGINE = AggregatingMergeTree()
ORDER BY timeslice POPULATE AS
SELECT DISTINCT
  id, toUInt64(FLOOR(timestamp/60)*60) AS timeslice, avgState(data) as aggregate
FROM storage.sensors_data
GROUP BY (id, timeslice);

create table storage.distr_minute_lens AS storage.minute_lens
ENGINE = Distributed(awesome_cluster, storage, minute_lens);
