################################################################################
## Development
################################################################################

# Runs the trades service as a standalone Pyton app (not Dockerized)
dev:
	uv run services/${service}/src/${service}/main.py

# Builds a docker image from a given Dockerfile
build-for-dev:
	@image_name=$$(echo ${service} | sed 's/_/-/g') && \
	docker build -t $${image_name}:dev -f docker/${service}.Dockerfile .

# Runs the docker image in a container on the local machine
run: build-for-dev
	docker run -it ${service}:dev

# Push the docker image to the docker registry of our kind cluster
push-for-dev:
	# Exercise: do not push to the kind local registry, but the one on your Github account
	@image_name=$$(echo ${service} | sed 's/_/-/g') && \
	kind load docker-image $${image_name}:dev --name rwml-34fa

# Deploys the docker image to the kind cluster
deploy-for-dev: build-for-dev push-for-dev
	kubectl delete -f deployment/dev/yamls/${service}.yaml --ignore-not-found=true
	kubectl apply -f deployment/dev/yamls/${service}.yaml

################################################################################
## Production
################################################################################
build-and-push-for-prod:
	@BUILD_DATE=$$(date +%s) && \
	docker buildx build --push \
    --platform linux/amd64 \
    -t ghcr.io/Real-World-ML/${service}:0.1.5-beta.$${BUILD_DATE}  \
    --label org.opencontainers.image.revision=$$(git rev-parse HEAD) \
    --label org.opencontainers.image.created=$$(date -u +%Y-%m-%dT%H:%M:%SZ) \
    --label org.opencontainers.image.url="https://github.com/Real-World-ML/real-time-ml-system-cohort-4/docker/${service}.Dockerfile" \
    --label org.opencontainers.image.title="${service}" \
    --label org.opencontainers.image.description="${service} Dockerfile" \
    --label org.opencontainers.image.licenses="" \
    --label org.opencontainers.image.source="https://github.com/Real-World-ML/real-time-ml-system-cohort-4" \
    -f docker/${service}.Dockerfile .

deploy-for-prod:
	kubectl delete -f deployments/prod/${service}/${service}.yaml --ignore-not-found=true
	kubectl apply -f deployments/prod/${service}/${service}.yaml

lint:
	ruff check . --fix