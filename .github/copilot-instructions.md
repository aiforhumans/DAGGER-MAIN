# Dagger Python Module Development Guide

## Project Architecture

This is a **comprehensive Dagger Python module** that integrates with Docker Model Runner (DMR) for AI/LLM functionality. The module serves as a reference implementation with 50+ functions covering all Dagger SDK patterns.

### Key Components
- **Module root**: `.dagger/` contains embedded Dagger Python SDK and module code
- **Module source**: `.dagger/src/my_module/main.py` with comprehensive function library
- **Configuration**: `dagger.json` defines module metadata and Python SDK
- **Environment**: `.env` configures DMR integration for LLM features

### Architecture Patterns
- **Single object type**: `MyModule` class contains all functions
- **Custom types**: `BuildResult` class demonstrates object chaining
- **Async-first**: All container I/O operations use `async`/`await`
- **Type safety**: Full type hints for all parameters and return types

## Essential Developer Workflows

### Module Development
```powershell
# Initialize new module (already done)
dagger init --name my-module
dagger develop --sdk=python

# List all available functions
dagger functions

# Get help for specific function
dagger call container-echo --help

# Test individual functions
dagger call greet --name="World"
dagger call calculate --a=10 --b=5 --operation="multiply"
```

### DMR + LLM Setup (Required for AI features)
```powershell
# Enable Docker Model Runner
docker desktop enable model-runner --tcp 12434

# Pull Gemma 3 model
docker model pull ai/gemma3

# Verify model availability
docker model ls

# Test LLM integration
dagger -c 'llm | model'
dagger -c 'llm | with-prompt "Hello" | last-reply'
```

### Function Testing Patterns
```powershell
# Basic function calls
dagger call container-echo --string-arg "test"

# Custom type chaining
dagger call create-build-result --source=. --language="python" | dagger call get-language

# Service operations
dagger call create-http-service --port=8080 | dagger call test-service-connectivity --port=8080

# Remote repository operations
dagger call clone-and-build-remote --repo-url="https://github.com/user/repo" --branch="main"
```

## Critical Implementation Patterns

### Function Structure
```python
@object_type
class MyModule:
    @function
    async def container_echo(self, string_arg: str) -> dagger.Container:
        """Returns a container that echoes the provided string"""
        return dag.container().from_("alpine:latest").with_exec(["echo", string_arg])

    @function
    def greet(self, name: str) -> str:
        """Returns a greeting (sync function for simple operations)"""
        return f"Hello, {name}!"
```

### Custom Object Types
```python
@object_type
class BuildResult:
    """Custom object type that supports method chaining"""
    language: str
    source: dagger.Directory

    @function
    def get_language(self) -> str:
        """Getter for the build language"""
        return self.language

    @function
    async def get_file_count(self) -> int:
        """Counts files in the source directory"""
        entries = await self.source.entries()
        return len(entries)
```

### LLM Integration
```python
@function
async def analyze_code_with_llm(self, source: dagger.Directory, query: str) -> str:
    """Uses LLM to analyze code in a directory"""
    # Get file contents
    files = await source.entries()
    code_content = ""
    for file in files[:3]:
        if file.endswith('.py'):
            file_obj = source.file(file)
            content = await file_obj.contents()
            code_content += f"\n--- {file} ---\n{content[:500]}..."

    prompt = f"Analyze this Python code:\n{code_content}\n\nQuery: {query}"
    return await dag.llm().with_prompt(prompt).last_reply()
```

### Git Operations
```python
@function
async def clone_and_build_remote(self, repo_url: str, branch: str) -> dagger.Container:
    """Clones a remote repository and builds it"""
    # Always use .branch() or .head() before .tree()
    source = dag.git(repo_url).branch(branch).tree()

    return (
        dag.container()
        .from_("golang:1.21")
        .with_mounted_directory("/src", source)
        .with_workdir("/src")
        .with_exec(["go", "mod", "download"])
        .with_exec(["go", "build", "-o", "/app", "."])
    )
```

### Service Integration
```python
@function
async def test_service_connectivity(self, service: dagger.Service, port: int) -> str:
    """Tests connectivity to a service"""
    return await (
        dag.container()
        .from_("alpine:latest")
        .with_exec(["apk", "add", "curl"])
        .with_service_binding("test-service", service)
        .with_exec(["curl", "-v", f"http://test-service:{port}/"])
        .stdout()
    )
```

## Project-Specific Conventions

### Function Signatures
- **Always use `@function` decorator** for all callable functions
- **Type hints required** for all parameters and return types
- **Detailed docstrings** with `Args:` sections for complex functions
- **Optional parameters**: Use `// +optional` comment (not type hints)
- **Default values**: Use `// +default="value"` comment (not function defaults)

### Container Operations
- **Forward slashes only** in container paths (even on Windows)
- **Async required** for any container I/O: `.stdout()`, `.entries()`, `.contents()`
- **Chain operations** fluently: `.from_().with_exec().with_mounted_directory()`
- **Use Alpine Linux** as base for simple operations

### Error Handling
```python
@function
async def handle_errors(self, operation: str) -> str:
    """Demonstrates error handling patterns"""
    try:
        if operation == "success":
            return "Operation completed successfully"
        # ... other operations
    except Exception as e:
        return f"Error occurred: {str(e)}"
```

### Cache Management
```python
@function
def create_cache_volume(self, name: str) -> dagger.CacheVolume:
    """Creates a cache volume for persistent caching"""
    return dag.cache_volume(name)

@function
async def build_with_cache(self, source: dagger.Directory, cache: dagger.CacheVolume) -> dagger.Container:
    """Builds with cache volume for faster rebuilds"""
    return (
        dag.container()
        .from_("golang:1.21")
        .with_mounted_cache("/go/pkg", cache)  # Mount cache first
        .with_mounted_directory("/src", source)
        .with_workdir("/src")
        .with_exec(["go", "mod", "download"])
        .with_exec(["go", "build", "-o", "/app", "."])
    )
```

## Integration Points

### Docker Model Runner (DMR)
- **Environment variables** loaded from `.env` file automatically
- **OpenAI-compatible API** at `http://model-runner.docker.internal/engines/v1/`
- **Gemma 3 model** configured as default: `index.docker.io/ai/gemma3`
- **Streaming disabled** for better compatibility: `OPENAI_DISABLE_STREAMING=true`

### External Dependencies
- **Git repositories** accessed via `dag.git().branch().tree()` pattern
- **Remote modules** referenced by GitHub URL with version tags
- **Container registries** for publishing built images
- **External services** bound via `with_service_binding()`

## Common Pitfalls & Solutions

### Dagger-Specific Issues
- **Don't edit `.dagger/sdk/`** - contains vendored Dagger SDK
- **Module functions must be decorated** with `@function`
- **Async functions require `await`** for Dagger operations
- **Container paths use forward slashes** even on Windows
- **Use `dagger functions`** to verify function availability

### DMR Integration Issues
- **Model not found**: Run `docker model pull ai/gemma3`
- **Connection failed**: Ensure DMR enabled with `docker desktop enable model-runner --tcp 12434`
- **Environment variables**: Must be in `.env` file in working directory

### Development Workflow
- **Test functions individually** with `dagger call <function> --help`
- **Check Dagger version** with `dagger version` for compatibility
- **Monitor execution traces** via Dagger's built-in tracing
- **Use Alpine containers** for simple operations to minimize image size

## Key Files Reference

- **`.dagger/src/my_module/main.py`**: Main module implementation (50+ functions)
- **`dagger.json`**: Module configuration and SDK specification
- **`.env`**: DMR and LLM environment configuration
- **`README.md`**: Project overview and setup instructions
- **`Commands.md`**: Essential CLI commands and usage examples

## Testing & Validation

### Function Testing
```powershell
# Test compilation
dagger functions

# Test individual functions
dagger call greet --name="Test"
dagger call calculate --a=5 --b=3 --operation="add"

# Test custom types
dagger call create-build-result --source=. --language="python"
```

### LLM Testing
```powershell
# Verify DMR connection
dagger -c 'llm | model'

# Test LLM functions
dagger call analyze-code-with-llm --source=. --query="What does this do?"
```

### Service Testing
```powershell
# Test service creation
dagger call create-http-service --port=8080

# Test service connectivity
dagger call test-service-connectivity --service=<service> --port=8080
```