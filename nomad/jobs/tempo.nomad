job "tempo" {
  datacenters = ["dc1"]
  type = "service"

  update {
    stagger = "30s"
    max_parallel = 1
  }

  group "tempo" {
    restart {
      attempts = 10
      interval = "5m"
      delay = "10s"
      mode = "delay"
    }
    network {
      port "http" {
          static = 3200
      }
      port "otlp-http" {
          static = 4318
      }
      port "otlp-grpc" {
          static = 4317
      }
    }
    task "tempo" {
      driver = "docker"
      config {
        image = "grafana/tempo:latest"
        ports = ["http", "otlp-grpc", "otlp-http"]
        args = ["-config.file=/etc/tempo.yaml"]
        volumes = [
          "local/tempo.yaml:/etc/tempo.yaml"
        ]
      }
      resources {
        cpu    = 1000
        memory = 256
      }
      service {
        name = "grafana-tempo"
        port = "http"
      }
      template {
        change_mode   = "signal"
        change_signal = "SIGINT"
        destination = "local/tempo.yaml"
        data = <<EOH
---
metrics_generator_enabled: true

server:
  http_listen_port: 3200

distributor:
  receivers:
    otlp:
      protocols:
        http:
        grpc:
  log_received_traces: true

ingester:
  trace_idle_period: 10s # the length of time after a trace has not received spans to consider it complete and flush it
  max_block_bytes: 1_000_000 # cut the head block when it hits this size or ...
  max_block_duration: 5m #   this much time passes

compactor:
  compaction:
    compaction_window: 1h # blocks in this time window will be compacted together
    max_block_bytes: 100_000_000 # maximum size of compacted blocks
    block_retention: 1h
    compacted_block_retention: 10m

metrics_generator:
  registry:
    external_labels:
      source: tempo
      cluster: dc-1
  storage:
    path: /tmp/tempo/generator/wal
    remote_write:
      - url: http://{{ env "NOMAD_IP_http" }}:9090/api/v1/write
        send_exemplars: true

storage:
  trace:
    backend: local # backend configuration to use
    block:
      bloom_filter_false_positive: .05 # bloom filter false positive rate.  lower values create larger filters but fewer false positives
      index_downsample_bytes: 1000 # number of bytes per index record
      encoding: zstd # block encoding/compression.  options: none, gzip, lz4-64k, lz4-256k, lz4-1M, lz4, snappy, zstd, s2
    wal:
      path: /tmp/tempo/wal # where to store the the wal locally
      encoding: snappy # wal encoding/compression.  options: none, gzip, lz4-64k, lz4-256k, lz4-1M, lz4, snappy, zstd, s2
    local:
      path: /tmp/tempo/blocks
    pool:
      max_workers: 100 # worker pool determines the number of parallel requests to the object store backend
      queue_depth: 10000

overrides:
  metrics_generator_processors: [service-graphs, span-metrics]
EOH
      }
    }
  }
}