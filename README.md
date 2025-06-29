# Crypto Predictor Production Proof of Concept

This repository contains a collection of services that together form a minimal production-ready system for cryptocurrency price prediction. The goal is to demonstrate how streaming market data can be collected, enriched with technical indicators, and used to train and serve predictive models.

## Purpose

The project showcases a microservice architecture that ingests raw trade data, aggregates it into candles, computes indicators, trains models and exposes predictions via an API. It is intended as a proof of concept for building a production system rather than a finished trading application.

## Services

- **trades** – fetches raw trade data and publishes it to Kafka.
- **candles** – aggregates trades into OHLC candles.
- **technical_indicators** – calculates indicators such as SMA and RSI.
- **predictor** – provides a training pipeline and model registry.
- **prediction-api** – (Rust) serves predictions from trained models.

Each service has its own Dockerfile in the `docker` directory and can be deployed individually.

## Deployment

Scripts under `deployment/` help spin up a local Kubernetes environment along with Kafka, RisingWave and observability tooling. The `Makefile` contains convenience targets for development and deployment.

---

This repository is experimental and meant for demonstration purposes only. It aims to provide a baseline for a production-ready setup that you can customize to fit your own requirements.
