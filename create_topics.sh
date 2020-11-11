docker run wurstmeister/kafka bash -c " 
    kafka-topics.sh --create \
        --zookeeper host.docker.internal:2181 \
        --topic telemetry \
        --partitions 2 \
        --replication-factor 2"