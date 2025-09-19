# Dagger Python Module Development Guide

## Project Overview

This is a **comprehensive Dagger Python module** with 50+ functions demonstrating all Dagger SDK patterns, plus Docker Model Runner (DMR) integration for AI/LLM functionality. Located in `.dagger/src/my_module/main.py` with embedded SDK in `.dagger/sdk/`.

## Essential Commands

```powershell
# Core development workflow
dagger functions                                    # List all available functions
dagger call <function> --help                     # Get function parameter help
dagger call greet --name="World"                  # Test simple functions
dagger call create-build-result --source=. --language="python" | dagger call get-language  # Test chaining

# DMR setup (required for LLM functions)
docker desktop enable model-runner --tcp 12434    # Enable Docker Model Runner
docker model pull ai/gemma3                       # Pull Gemma 3 model
dagger -c 'llm | model'                          # Verify LLM integration
```

## Critical Implementation Patterns

**Function Requirements:**

- Always use `@function` decorator for callable functions
- Use `async def` for any container I/O operations (`.stdout()`, `.entries()`, `.contents()`)
- Required type hints: `dagger.Container`, `dagger.Directory`, `str`, etc.
- Optional parameters: `// +optional` comment, Default values: `// +default="value"` comment

**Platform Conventions:**

- **Always use forward slashes** in container paths (even on Windows)
- **Git operations**: Must use `dag.git(url).branch(name).tree()` or `.head().tree()` pattern
- **Alpine base**: Use `dag.container().from_("alpine:latest")` for simple operations
- **Service binding**: Use `with_service_binding("name", service)` for inter-service communication

**Essential Pattern Example:**

```python
@object_type
class MyModule:
    @function
    async def container_echo(self, string_arg: str) -> dagger.Container:
        return dag.container().from_("alpine:latest").with_exec(["echo", string_arg])
    
    @function
    async def clone_and_build(self, repo_url: str, branch: str) -> dagger.Container:
        source = dag.git(repo_url).branch(branch).tree()  # Critical: .branch() before .tree()
        return dag.container().from_("golang:1.21").with_mounted_directory("/src", source)
```

## Integration & Environment

**DMR Configuration** (`.env` file):

- `OPENAI_BASE_URL=http://model-runner.docker.internal/engines/v1/`
- `OPENAI_MODEL=index.docker.io/ai/gemma3`
- `OPENAI_DISABLE_STREAMING=true`

**LLM Usage**: Access via `await dag.llm().with_prompt(prompt).last_reply()`

## Common Pitfalls

- **Never edit `.dagger/sdk/`** - contains vendored Dagger SDK
- **Missing `@function` decorator** - functions won't appear in `dagger functions`
- **Forgetting `await`** - all Dagger I/O operations are async
- **Wrong path separators** - use `/` not `\` in container paths
- **Git API errors** - always call `.branch()` or `.head()` before `.tree()`
- **Missing DMR setup** - run `docker model pull ai/gemma3` if LLM functions fail

## Key Files

- `.dagger/src/my_module/main.py` - Main module (50+ function examples)
- `dagger.json` - Module configuration and SDK version
- `.env` - DMR/LLM environment variables
- `Commands.md` - Additional CLI examples and patterns
