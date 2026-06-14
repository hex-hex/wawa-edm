#!/usr/bin/env bash
#
# release.sh — build the Docker image and push it to Docker Hub
#              (wawaassistant/wawa-edm).
#
# Usage:
#   ./release.sh [TAG]
#
#   TAG  image tag to publish. Defaults to the version in pyproject.toml.
#        The image is always pushed as :latest as well.
#
# Environment overrides:
#   IMAGE     full repository name        (default: wawaassistant/wawa-edm)
#   PLATFORM  target build platform(s)    (default: linux/amd64)
#
# Note: run `docker login` once beforehand so the push is authenticated.
#
set -euo pipefail

# Always operate from the repo root (where the Dockerfile lives).
cd "$(dirname "$0")"

IMAGE="${IMAGE:-wawaassistant/wawa-edm}"
PLATFORM="${PLATFORM:-linux/amd64}"

# Tag: first CLI arg, otherwise the project version from pyproject.toml.
if [ "$#" -ge 1 ]; then
  TAG="$1"
else
  TAG="$(grep -E '^version = ' pyproject.toml | head -1 | sed -E 's/^version = "(.*)"/\1/')"
fi

if [ -z "${TAG:-}" ]; then
  echo "error: could not determine a tag (pass one as the first argument)" >&2
  exit 1
fi

echo "==> Building ${IMAGE}:${TAG} (and :latest) for ${PLATFORM}"

# buildx builds for the target platform and pushes in a single step, so an
# image built on an arm64 Mac still runs on amd64 Linux servers.
docker buildx build \
  --platform "${PLATFORM}" \
  --tag "${IMAGE}:${TAG}" \
  --tag "${IMAGE}:latest" \
  --push \
  .

echo "==> Done. Pushed ${IMAGE}:${TAG} and ${IMAGE}:latest"
