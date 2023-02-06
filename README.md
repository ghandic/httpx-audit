# Audit Trail Demo

Basic example of how to make use of request/response hooks to store, obfuscate, and log request/response information using httpx

```shell
make init
make demo
```

## Full observability demo

Basic example of a API with trace/log/metric collection using opentelemetry and the above httpx auditing demo.

```shell
make init
# Now add your datadog API key (can be a free license) to your .env file
make up # or `make up/debug` and attach your vscode debugger
```

## Make commands

```text
build                          Builds the local demo application
clean                          Removes junk build, test, coverage and Python artifacts
demo                           Runs the basic cli demo
fmt                            Formats Python code to align with standards defined in pyproject.toml
init                           Initialize project with dev requirements
up/debug                       Builds and starts the whole application stack with debugger attached
up                             Builds and starts the whole application stack
```
