# Dagger Python Module Development Guide

## Project Architecture

This is a **Dagger Python module** that integrates with Docker Model Runner (DMR) for AI/LLM functionality. The project structure follows Dagger's module conventions:

- **Module root**: `.dagger/` contains the actual module code
- **Module source**: `.dagger/src/my_module/` with Python package structure
- **SDK embedding**: `.dagger/sdk/` contains the complete Dagger Python SDK
- **Configuration**: `dagger.json` defines module metadata and SDK version

## Quick Start: From Zero to Hero

### 1. Initialize a Module
```powershell
# In your repo root
dagger init --name my-module
dagger develop --sdk=python
```
This creates `dagger.json` and sample functions. Use `dagger functions` to see all callable functions.

### 2. Call Functions from CLI
```powershell
# Single function
dagger call greet --name="Ada"

# Chained pipeline
dagger -c 'container | from alpine | with-exec "uname" "-a" | stdout'

# Remote module
dagger -m github.com/owner/repo@v1.2.3 call build --source=https://github.com/foo/bar#main:/subdir
```

### 3. Define Functions
```python
from dagger import dag, function, object_type

@object_type
class MyModule:
    @function
    async def greet(self, name: str) -> str:
        return f"Hello, {name}"
```

## Key Development Patterns

### Module Function Structure
Functions in `.dagger/src/my_module/main.py` follow this pattern:
```python
@object_type
class MyModule:
    @function
    def container_echo(self, string_arg: str) -> dagger.Container:
        return dag.container().from_("alpine:latest").with_exec(["echo", string_arg])
```

### Advanced Function Patterns
- **Optional parameters**: Use `// +optional` comment for CLI-optional args
- **Default values**: Use `// +default="value"` comment for parameter defaults
- **Array parameters**: Use `list[str]` for multiple values
- **Async functions**: Always use `async`/`await` for container I/O operations
- **Documentation**: Use `Doc()` for parameter descriptions

### Arguments (CLI flags ↔ typed args)
```powershell
# Scalars
dagger call greet --name="Ada" --count=3 --verbose=true

# Files/Directories (local or remote)
dagger call analyze-dir --dir=./src
dagger call analyze-dir --dir=https://github.com/dagger/dagger#main:/cmd

# Services
dagger call connect-db --service=tcp://localhost:5432

# Sockets
dagger call build --docker=/var/run/docker.sock
```

### Return Types
```python
# String/int/float → printed to stdout
@function
def greet(self, name: str) -> str:
    return f"Hello, {name}"

# File → export to host
@function
def create_file(self, content: str) -> dagger.File:
    return dag.directory().with_new_file("output.txt", content).file("output.txt")

# Directory → export directory
@function
def create_docs(self) -> dagger.Directory:
    return dag.directory().with_new_file("README.md", "# Docs")

# Container → chain more operations
@function
def build_app(self) -> dagger.Container:
    return dag.container().from_("python:3.11").with_exec(["echo", "built"])

# Service → long-running background service
@function
def start_server(self) -> dagger.Service:
    return dag.container().from_("nginx").as_service()
```

### Container Building Patterns
- Use `dag.container().from_("base:image")` for base containers
- Chain operations: `.with_exec()`, `.with_mounted_directory()`, `.with_workdir()`
- Prefer `Directory.docker_build()` over deprecated `Container.build()`

## Essential Commands

### Module Development
```powershell
# Initialize new module
dagger init --name my-module
dagger develop --sdk=python

# List all functions
dagger functions

# Get help for specific function
dagger call container-echo --help

# Test functions
dagger call greet --name="World"
dagger call calculate --a=10 --b=5 --operation="multiply"
```

### Docker Model Runner Setup
```powershell
# Enable DMR with TCP access
docker desktop enable model-runner --tcp 12434

# Pull AI models
docker model pull ai/gemma3
docker model ls
```

### LLM Integration with Gemma 3
```powershell
# Configure environment
export OPENAI_BASE_URL=http://model-runner.docker.internal/engines/v1/
export OPENAI_MODEL=index.docker.io/ai/gemma3
export OPENAI_DISABLE_STREAMING=true

# Use LLM from CLI
dagger -c 'llm | with-prompt "What tools do you have available?" | last-reply'
```

## Advanced Patterns

### Chaining Custom Functions
```powershell
# Chain custom functions like core API
dagger -m github.com/kpenfound/dagger-modules/golang@v0.2.1 -c \
'build . --source=https://github.com/golang/example#master:/hello | directory . | entries'
```

### Secrets (Safe Usage)
```powershell
# From environment
export API_TOKEN="secret"
dagger -c 'container | from alpine | with-secret-variable MY_SECRET env://API_TOKEN | with-exec -- sh -c "echo $MY_SECRET" | stdout'

# In functions
@function
async def use_secret(self, token: dagger.Secret) -> str:
    return await dag.container().from_("alpine") \
        .with_secret_variable("TOKEN", token) \
        .with_exec(["sh", "-c", "echo $TOKEN"]) \
        .stdout()
```

### Services (Background Processes)
```powershell
# Start service and expose to host
dagger -c 'http-service | up'
dagger -c 'http-service | up --ports 9000:8080'

# Use service in functions
@function
async def test_service(self, svc: dagger.Service) -> str:
    return await dag.container().from_("alpine") \
        .with_service_binding("test-svc", svc) \
        .with_exec(["curl", "http://test-svc"]) \
        .stdout()
```

### Cache Volumes (Performance)
```powershell
# Mount persistent cache
dagger -c 'container | from node:21 | with-directory /src . | with-workdir /src | with-mounted-cache /root/.npm node-21 | with-exec npm install'

# In functions
@function
def build_with_cache(self, source: dagger.Directory, cache: dagger.CacheVolume) -> dagger.Container:
    return dag.container().from_("golang:1.21") \
        .with_mounted_cache("/go/pkg", cache) \
        .with_mounted_directory("/src", source) \
        .with_workdir("/src") \
        .with_exec(["go", "build", "-o", "/app", "."])
```

### Error Handling
```python
@function
def divide(self, a: int, b: int) -> float:
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
```

### Remote Repositories & Dependencies
```powershell
# Use remote directories
dagger call build --source=https://github.com/user/repo#v1.2.3:/src

# Install module dependencies
dagger install github.com/acme/tools@v0.4.0

# Use remote modules
dagger -m github.com/owner/repo@v1.0.0 call publish --image ghcr.io/owner/app
```

## Project-Specific Conventions

### Package Structure
- Module name in `dagger.json` should match `.dagger/src/{module_name}/`
- Main class typically named after module (e.g., `MyModule`)
- Use `from .main import MyModule as MyModule` in `__init__.py`

### Dependencies & Environment
- **uv** is preferred over pip for package management
- **Python 3.13+** required (see `pyproject.toml`)
- SDK is embedded and editable in `.dagger/sdk/`

### Function Signatures
- Use type hints: `dagger.Container`, `dagger.Directory`, `str`, etc.
- Async functions for I/O operations: `await container.stdout()`
- Return Dagger types for chainability

## Integration Points

### LLM/AI Features
- Access via `dag.llm()` with model configuration from environment
- DMR provides OpenAI-compatible endpoints
- Model configuration in `.env`: `OPENAI_MODEL=index.docker.io/ai/gemma3`

### Container Execution
- All execution happens in containers via Dagger Engine
- Network access to `model-runner.docker.internal` from containers
- Host access to `localhost:12434` (if TCP enabled)

## Testing & Debugging
- Use `dagger call` for testing individual functions
- Check `dagger version` for engine compatibility
- Monitor container logs via Dagger's execution tracing
- DMR model availability: `docker model ls`

## Common Pitfalls
- Don't edit files in `.dagger/sdk/` - they're generated/vendored
- Module functions must be decorated with `@function`
- Async functions require `await` for Dagger operations
- Container paths use forward slashes even on Windows
- Use `dagger functions` to see all available functions
- Use `dagger call <func> --help` for parameter help