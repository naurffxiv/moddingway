# Moddingway
[![Build](https://github.com/naurffxiv/moddingway/actions/workflows/build-code.yml/badge.svg?branch=main&event=push)](https://github.com/naurffxiv/moddingway/actions/workflows/build-code.yml)
[![Lint](https://github.com/naurffxiv/moddingway/actions/workflows/lint-code.yml/badge.svg?branch=main&event=push)](https://github.com/naurffxiv/moddingway/actions/workflows/lint-code.yml)
[![Test](https://github.com/naurffxiv/moddingway/actions/workflows/test-code.yml/badge.svg?branch=main&event=push)](https://github.com/naurffxiv/moddingway/actions/workflows/test-code.yml)

## What is Moddingway?
Moddingway is a moderation bot and API for the [NAUR](https://naurffxiv.com/) Discord server.

## Getting started
To start developing Moddingway you need just a few things:

- [.NET 10 SDK](https://dotnet.microsoft.com/en-us/download/dotnet/10.0)
- [Aspire CLI](https://aspire.dev/get-started/install-cli/)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/), [Podman Desktop](https://podman-desktop.io/), or [Rancher Desktop](https://rancherdesktop.io/)
- [UV](https://docs.astral.sh/uv/getting-started/installation/)

## Run Moddingway
Once you have all the dependencies listed above simply execute `aspire run` to start Moddingway. You can access the following services:

- Aspire Dashbord: https://aspire.dev.localhost:8440
- Moddingway API: https://moddingway.dev.localhost:8443

The Aspire dashboard may prompt for additional values in order to start moddingway, these are usualy specific to your discord server.
