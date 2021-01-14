CREATE database IF NOT EXISTS storage;

CREATE TABLE IF NOT EXISTS storage.queue (
    id UInt32,
    timestamp UInt64,
    data Float64
  ) ENGINE = Kafka()
SETTINGS
    kafka_broker_list = 'kafka-1:19093,kafka-2:29093,kafka-3:39093',
    kafka_topic_list = 'telemetry',
    kafka_group_name = 'telemetry-group',
    kafka_format = 'JSONEachRow';

CREATE TABLE IF NOT EXISTS storage.sensors_data (
    id UInt32,
    timestamp UInt64,
    data Float64
) ENGINE = ReplicatedReplacingMergeTree("/clickhouse/tables/{shard}/sensors_data", "{replica_name}")
ORDER BY (timestamp, id, data); -- in ReplacingMergeTree uniqueness is defined by order by key

CREATE MATERIALIZED VIEW IF NOT EXISTS storage.queue_mv TO storage.sensors_data
  AS SELECT * FROM storage.queue;

CREATE table storage.sensors_all as storage.sensors_data
Engine = Distributed(awesome_cluster, storage, sensors_data, rand());


CREATE MATERIALIZED VIEW IF NOT EXISTS storage.minute_lens
ENGINE = ReplicatedAggregatingMergeTree("/clickhouse/tables/{shard}/minute_lens", "{replica_name}")
ORDER BY timeslice POPULATE AS
SELECT DISTINCT
  id, toUInt64(FLOOR(timestamp/60)*60) AS timeslice, avgState(data) as aggregate
FROM storage.sensors_data
GROUP BY (id, timeslice);

create table storage.distr_minute_lens AS storage.minute_lens
ENGINE = Distributed(awesome_cluster, storage, minute_lens);


CREATE MATERIALIZED VIEW IF NOT EXISTS storage.ten_minute_lens
ENGINE = ReplicatedAggregatingMergeTree("/clickhouse/tables/{shard}/ten_minute_lens", "{replica_name}")
ORDER BY timeslice POPULATE AS
SELECT DISTINCT
  id, toUInt64(FLOOR(timestamp/600)*600) AS timeslice, avgState(data) as aggregate
FROM storage.sensors_data
GROUP BY (id, timeslice);

create table storage.distr_ten_minute_lens AS storage.ten_minute_lens
ENGINE = Distributed(awesome_cluster, storage, ten_minute_lens);


CREATE MATERIALIZED VIEW IF NOT EXISTS storage.hour_lens
ENGINE = ReplicatedAggregatingMergeTree("/clickhouse/tables/{shard}/hour_lens", "{replica_name}")
ORDER BY timeslice POPULATE AS
SELECT DISTINCT
  id, toUInt64(FLOOR(timestamp/3600)*3600) AS timeslice, avgState(data) as aggrregate
FROM storage.sensors_data
GROUP BY (id, timeslice);

create table storage.distr_hour_lens AS storage.hour_lens
ENGINE = Distributed(awesome_cluster, storage, hour_lens);
