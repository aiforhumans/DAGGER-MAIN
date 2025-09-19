# Dagger Module Commands

This document contains essential commands for working with the Dagger module in this project.

## Module Functions

### List all functions

```powershell
dagger functions
```

### Get help for a specific function

```powershell
dagger call container-echo --help
```

### Test the functions

```powershell
# Test container-echo function
dagger call container-echo --string-arg "Hello World"

# Test grep-dir function
dagger call grep-dir --directory-arg . --pattern "dagger"

# Test greet function (simple string return)
dagger call greet --name="World"

# Test calculate function (multiple parameters)
dagger call calculate --a=10 --b=5 --operation="multiply"

# Test get-file-info function (directory + file parameters)
dagger call get-file-info --directory-arg=. --file-path="README.md"

# Test create-text-file function (creates a file)
dagger call create-text-file --content="Hello Dagger!" --filename="hello.txt"
```

## Pipeline Syntax Examples

### Basic pipeline with built-in operations

```powershell
dagger -c 'container | from alpine | with-exec "echo" "Hello from pipeline!" | stdout'
```

### Chaining on module function results

```powershell
# Call our function and chain methods on the result
dagger call container-echo --string-arg "Pipeline test" | dagger -c 'with-exec "echo" "Added via chaining" | stdout'
```

### Complex pipeline example

```powershell
dagger -c 'container | from alpine | with-exec "uname" "-a" | stdout'
```

## LLM Integration Commands

### Check current model

```powershell
dagger -c 'llm | model'
```

### Get a response from Gemma 3

```powershell
dagger -c 'llm | with-prompt "Reply with: hello from Gemma3" | last-reply'
```

### Force a specific model

```powershell
dagger -c 'llm | with-model "index.docker.io/ai/gemma3" | with-prompt "Your prompt here" | last-reply'
```

## Docker Model Runner Commands

### Enable Model Runner

```powershell
docker desktop enable model-runner --tcp 12434
```

### Pull Gemma 3 model

```powershell
docker model pull ai/gemma3
```

### List available models

```powershell
docker model ls
```

## Development Commands

### Initialize module (already done)

```powershell
dagger init --name my-module
dagger develop --sdk=python
```

### Check Dagger version

```powershell
dagger version
```

## Function Patterns Demonstrated

### Simple Functions

- **`greet`**: Basic string input/output function
- **`calculate`**: Multiple parameters with different types (int, string)

### Container Operations

- **`container-echo`**: Returns a container that can be further chained
- **`get-file-info`**: Uses containers to perform file system operations
- **`build-simple-app`**: Demonstrates building applications in containers

### File Operations

- **`create-text-file`**: Creates files and returns file objects
- **`grep-dir`**: Searches through directories using containerized tools

### Async Functions

- **`grep-dir`**: Uses `async/await` for I/O operations
- **`get-file-info`**: Asynchronous container execution
- **`build-simple-app`**: Async container building operations