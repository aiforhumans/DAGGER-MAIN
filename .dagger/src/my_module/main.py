import dagger
from dagger import dag, function, object_type, Doc
from enum import Enum
from typing import Optional


# ===== CUSTOM TYPES =====

@object_type
class BuildResult:
    """Custom object type that can be chained"""
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

    @function
    def with_language(self, new_language: str) -> "BuildResult":
        """Returns a new BuildResult with updated language"""
        return BuildResult(language=new_language, source=self.source)


@object_type
class MyModule:
    @function
    def container_echo(self, string_arg: str) -> dagger.Container:
        """Returns a container that echoes whatever string argument is provided"""
        return dag.container().from_("alpine:latest").with_exec(["echo", string_arg])

    @function
    async def grep_dir(self, directory_arg: dagger.Directory, pattern: str) -> str:
        """Returns lines that match a pattern in the files of the provided Directory"""
        return await (
            dag.container()
            .from_("alpine:latest")
            .with_mounted_directory("/mnt", directory_arg)
            .with_workdir("/mnt")
            .with_exec(["grep", "-R", pattern, "."])
            .stdout()
        )

    @function
    def greet(self, name: str) -> str:
        """Returns a personalized greeting message"""
        return f"Hello, {name}!"

    @function
    def greet_optional(self, name: str, prefix: str) -> str:  # +optional
        """Returns a greeting with optional prefix"""
        if prefix:
            return f"{prefix} {name}!"
        return f"Hello {name}!"

    @function
    def calculate(self, a: int, b: int, operation: str) -> int:
        """Performs basic arithmetic operations"""
        if operation == "add":
            return a + b
        elif operation == "subtract":
            return a - b
        elif operation == "multiply":
            return a * b
        elif operation == "divide":
            return a // b
        else:
            return 0

    @function
    def calculate_with_default(self, a: int, b: int, operation: str) -> int:  # +default="add"
        """Performs arithmetic with default operation"""
        if operation == "add":
            return a + b
        elif operation == "subtract":
            return a - b
        elif operation == "multiply":
            return a * b
        elif operation == "divide":
            return a // b
        else:
            return 0

    @function
    async def get_file_info(self, directory_arg: dagger.Directory, file_path: str) -> str:
        """Gets information about a file using container operations"""
        return await (
            dag.container()
            .from_("alpine:latest")
            .with_mounted_directory("/mnt", directory_arg)
            .with_workdir("/mnt")
            .with_exec(["ls", "-la", file_path])
            .stdout()
        )

    @function
    async def create_and_export_file(self, content: str, filename: str) -> str:
        """Creates a text file and exports it to the current working directory"""
        # Create the file
        file_obj = dag.directory().with_new_file(filename, content).file(filename)

        # Export to current working directory
        await file_obj.export(".")

        return f"File '{filename}' exported to current directory"

    @function
    def create_text_file(self, content: str, filename: str) -> dagger.File:
        """Creates a text file with the given content"""
        return dag.directory().with_new_file(filename, content).file(filename)

    @function
    async def build_simple_app(self, source_dir: dagger.Directory) -> dagger.Container:
        """Builds a simple application from source"""
        return (
            dag.container()
            .from_("python:3.11-slim")
            .with_mounted_directory("/src", source_dir)
            .with_workdir("/src")
            .with_exec(["pip", "install", "-r", "requirements.txt"])
        )

    @function
    def process_array(self, items: list[str], separator: str) -> str:  # +default=","
        """Joins array items with separator"""
        return separator.join(items)

    @function
    def boolean_logic(self, a: bool, b: bool, operation: str) -> bool:  # +default="and"
        """Performs boolean operations"""
        if operation == "and":
            return a and b
        elif operation == "or":
            return a or b
        elif operation == "xor":
            return a != b
        else:
            return False

    @function
    def float_operations(self, a: float, b: float, operation: str) -> float:  # +default="add"
        """Performs floating-point operations"""
        if operation == "add":
            return a + b
        elif operation == "subtract":
            return a - b
        elif operation == "multiply":
            return a * b
        elif operation == "divide":
            return a / b
        else:
            return 0.0

    @function
    async def use_secret(self, secret: dagger.Secret) -> str:
        """Demonstrates secret usage in containers"""
        return await (
            dag.container()
            .from_("alpine:latest")
            .with_secret_variable("MY_SECRET", secret)
            .with_exec(["sh", "-c", "echo 'Secret value: $MY_SECRET'"])
            .stdout()
        )

    @function
    async def use_service(self, service: dagger.Service) -> str:
        """Demonstrates service integration"""
        return await (
            dag.container()
            .from_("alpine:latest")
            .with_service_binding("my-service", service)
            .with_exec(["sh", "-c", "curl http://my-service"])
            .stdout()
        )

    @function
    def create_service_container(self, port: int) -> dagger.Container:
        """Creates a container that can be used as a service"""
        return (
            dag.container()
            .from_("nginx:alpine")
            .with_exposed_port(port)
        )

    @function
    def create_service_from_container(self, container: dagger.Container) -> dagger.Service:
        """Converts a container to a service"""
        return container.as_service()

    @function
    async def multi_step_build(self, source: dagger.Directory) -> dagger.Container:
        """Demonstrates multi-step container building"""
        # Start with base image
        ctr = dag.container().from_("python:3.11-slim")

        # Install system dependencies
        ctr = ctr.with_exec(["apt-get", "update"])
        ctr = ctr.with_exec(["apt-get", "install", "-y", "git", "curl"])

        # Mount source and install Python dependencies
        ctr = ctr.with_mounted_directory("/app", source)
        ctr = ctr.with_workdir("/app")
        ctr = ctr.with_exec(["pip", "install", "-r", "requirements.txt"])

        return ctr

    @function
    async def build_and_test(self, source: dagger.Directory) -> str:
        """Builds and runs tests in a container"""
        result = await (
            dag.container()
            .from_("python:3.11-slim")
            .with_mounted_directory("/app", source)
            .with_workdir("/app")
            .with_exec(["pip", "install", "-r", "requirements.txt"])
            .with_exec(["python", "-m", "pytest", "tests/", "-v"])
            .stdout()
        )
        return result

    @function
    def create_directory_with_files(self, filenames: list[str], contents: list[str]) -> dagger.Directory:
        """Creates a directory with multiple files"""
        directory = dag.directory()

        # Pair filenames with contents
        for filename, content in zip(filenames, contents):
            directory = directory.with_new_file(filename, content)

        return directory

    @function
    async def archive_directory(self, source: dagger.Directory, format: str) -> dagger.File:  # +default="tar.gz"
        """Creates an archive of a directory"""
        if format == "tar.gz":
            return await (
                dag.container()
                .from_("alpine:latest")
                .with_mounted_directory("/src", source)
                .with_workdir("/src")
                .with_exec(["tar", "czf", "/archive.tar.gz", "."])
                .file("/archive.tar.gz")
            )
        elif format == "zip":
            return await (
                dag.container()
                .from_("alpine:latest")
                .with_exec(["apk", "add", "zip"])
                .with_mounted_directory("/src", source)
                .with_workdir("/src")
                .with_exec(["zip", "-r", "/archive.zip", "."])
                .file("/archive.zip")
            )
        else:
            # Default to tar.gz
            return await (
                dag.container()
                .from_("alpine:latest")
                .with_mounted_directory("/src", source)
                .with_workdir("/src")
                .with_exec(["tar", "czf", "/archive.tar.gz", "."])
                .file("/archive.tar.gz")
            )

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
            .with_mounted_cache("/go/pkg", cache)
            .with_mounted_directory("/src", source)
            .with_workdir("/src")
            .with_exec(["go", "mod", "download"])
            .with_exec(["go", "build", "-o", "/app", "."])
        )

    @function
    async def handle_errors(self, operation: str) -> str:
        """Demonstrates error handling patterns"""
        try:
            if operation == "success":
                return "Operation completed successfully"
            elif operation == "container_error":
                # This will succeed
                result = await dag.container().from_("alpine:latest").with_exec(["echo", "success"]).stdout()
                return result
            elif operation == "invalid_command":
                # This will fail but we'll catch it
                result = await dag.container().from_("alpine:latest").with_exec(["invalid_command"]).stdout()
                return result
            else:
                return f"Unknown operation: {operation}"
        except Exception as e:
            return f"Error occurred: {str(e)}"

    @function
    def chain_example(self, base: str, modifier: str) -> "MyModule":
        """Returns self for chaining - stores state for later use"""
        # In a real implementation, you'd store state
        # For demo purposes, we'll just return self
        return self

    @function
    def get_chain_result(self) -> str:
        """Gets the result of a chained operation"""
        return "Chained operation result"

    @function
    async def publish_container(self, container: dagger.Container, registry: str, tag: str) -> str:
        """Publishes a container to a registry"""
        address = f"{registry}:{tag}"
        result = await container.publish(address)
        return f"Published to: {result}"

    @function
    async def export_container(self, container: dagger.Container, path: str) -> str:
        """Exports a container as an OCI tarball"""
        await container.export(path)
        return f"Container exported to: {path}"

    @function
    async def inspect_directory(self, directory: dagger.Directory) -> str:
        """Inspects directory contents"""
        entries = await directory.entries()
        return f"Directory contains: {', '.join(entries)}"

    @function
    async def read_file_content(self, file: dagger.File) -> str:
        """Reads file content"""
        return await file.contents()

    @function
    async def get_file_size(self, file: dagger.File) -> int:
        """Gets file size"""
        return await file.size()

    @function
    async def search_and_replace(self, source: dagger.Directory, pattern: str, replacement: str, file_pattern: str) -> dagger.Directory:
        """Performs search and replace across files in a directory"""
        return await (
            dag.container()
            .from_("alpine:latest")
            .with_exec(["apk", "add", "sed"])
            .with_mounted_directory("/src", source)
            .with_workdir("/src")
            .with_exec(["find", ".", "-name", file_pattern, "-exec", "sed", "-i", f"s/{pattern}/{replacement}/g", "{}", ";"])
            .directory("/src")
        )

    @function
    async def run_linter(self, source: dagger.Directory, linter: str) -> str:  # +default="flake8"
        """Runs a linter on source code"""
        if linter == "flake8":
            return await (
                dag.container()
                .from_("python:3.11")
                .with_mounted_directory("/src", source)
                .with_workdir("/src")
                .with_exec(["pip", "install", "flake8"])
                .with_exec(["flake8", "--max-line-length=100", "."])
                .stdout()
            )
        elif linter == "pylint":
            return await (
                dag.container()
                .from_("python:3.11")
                .with_mounted_directory("/src", source)
                .with_workdir("/src")
                .with_exec(["pip", "install", "pylint"])
                .with_exec(["pylint", "--disable=C0114,C0115,C0116", "."])
                .stdout()
            )
        else:
            return f"Unsupported linter: {linter}"

    @function
    async def generate_docs(self, source: dagger.Directory) -> dagger.Directory:
        """Generates documentation from source code"""
        return await (
            dag.container()
            .from_("python:3.11")
            .with_mounted_directory("/src", source)
            .with_workdir("/src")
            .with_exec(["pip", "install", "sphinx", "sphinx-rtd-theme"])
            .with_exec(["sphinx-build", "-b", "html", "docs", "docs/_build"])
            .directory("/src/docs/_build")
        )

    @function
    async def deploy_to_service(self, container: dagger.Container, service_name: str) -> dagger.Service:
        """Deploys a container as a service"""
        service = container.as_service()
        # In a real scenario, you might register the service or perform additional setup
        return service

    @function
    async def health_check(self, service: dagger.Service, endpoint: str) -> str:  # +default="/health"
        """Performs health check on a service"""
        return await (
            dag.container()
            .from_("alpine:latest")
            .with_exec(["apk", "add", "curl"])
            .with_service_binding("target-service", service)
            .with_exec(["curl", "-f", f"http://target-service{endpoint}"])
            .stdout()
        )

    @function
    def create_multi_stage_build(self) -> dagger.Container:
        """Demonstrates multi-stage build pattern"""
        # Build stage
        build_stage = (
            dag.container()
            .from_("golang:1.21")
            .with_directory("/src", dag.git("https://github.com/golang/example").branch("master").tree())
            .with_workdir("/src/hello")
            .with_exec(["go", "build", "-o", "/hello", "."])
        )

        # Runtime stage
        runtime_stage = (
            dag.container()
            .from_("alpine:latest")
            .with_file("/hello", build_stage.file("/hello"))
            .with_exec(["chmod", "+x", "/hello"])
        )

        return runtime_stage

    # ===== ENUMERATIONS =====

    @function
    def process_with_enum(self, operation: str, value: int) -> str:  # +default="double"
        """Demonstrates enum-like constrained string choices"""
        if operation == "double":
            return f"Double of {value} is {value * 2}"
        elif operation == "square":
            return f"Square of {value} is {value ** 2}"
        elif operation == "cube":
            return f"Cube of {value} is {value ** 3}"
        else:
            return f"Unknown operation: {operation}. Use: double, square, or cube"

    # ===== CUSTOM TYPES & INTERFACES =====

    @function
    def create_build_result(self, source: dagger.Directory, language: str) -> "BuildResult":
        """Returns a custom object that can be chained"""
        # This would return a custom BuildResult object in a real implementation
        # For demo purposes, we'll return a simple result
        return BuildResult(language=language, source=source)

    @function
    def get_build_status(self) -> str:
        """Getter for build status (demonstrates state)"""
        return "Build completed successfully"

    # ===== LLM INTEGRATION =====

    @function
    async def analyze_code_with_llm(self, source: dagger.Directory, query: str) -> str:
        """Uses LLM to analyze code in a directory"""
        # Get file contents
        files = await source.entries()
        code_content = ""
        for file in files[:3]:  # Limit to first 3 files for demo
            if file.endswith('.py'):
                file_obj = source.file(file)
                content = await file_obj.contents()
                code_content += f"\n--- {file} ---\n{content[:500]}..."  # Limit content

        prompt = f"Analyze this Python code:\n{code_content}\n\nQuery: {query}"

        # Use LLM for analysis
        llm_result = await dag.llm().with_prompt(prompt).last_reply()
        return llm_result

    @function
    async def generate_code_with_llm(self, description: str, language: str) -> dagger.File:
        """Uses LLM to generate code based on description"""
        prompt = f"Generate {language} code for: {description}. Return only the code, no explanations."

        code = await dag.llm().with_prompt(prompt).last_reply()

        # Clean up the response (remove markdown code blocks if present)
        if "```" in code:
            # Extract code from markdown blocks
            lines = code.split('\n')
            in_code_block = False
            clean_code = []
            for line in lines:
                if line.startswith('```'):
                    in_code_block = not in_code_block
                    continue
                if in_code_block:
                    clean_code.append(line)
            code = '\n'.join(clean_code)

        return dag.directory().with_new_file(f"generated.{language}", code).file(f"generated.{language}")

    # ===== INLINE DOCUMENTATION =====

    @function
    def greet_with_docs(self, name: str, style: str) -> str:
        """Enhanced greeting function with detailed documentation

        Args:
            name: Who to greet
            style: Greeting style (formal or casual)
        """
        if style == "formal":
            return f"Good day, {name}!"
        elif style == "casual":
            return f"Hey {name}!"
        else:
            return f"Hello {name}!"

    # ===== API PLAYGROUND EXAMPLES =====

    @function
    async def raw_graphql_query(self, query: str) -> str:
        """Demonstrates raw GraphQL queries (normally done via dagger query)"""
        # This function shows how you could execute raw GraphQL from within a function
        # In practice, you'd use dagger query from CLI for this
        return f"Raw GraphQL query: {query}\n\nTo execute this, use: dagger query --doc '{query}'"

    # ===== ENHANCED STATE MANAGEMENT =====

    @function
    def configure_builder(self, registry: str, tag_prefix: str) -> "MyModule":
        """Module constructor - configures module-wide settings

        Args:
            registry: Container registry URL
            tag_prefix: Tag prefix for builds
        """
        # In a real implementation, this would store configuration in the object
        # For demo purposes, we'll just return self
        return self

    @function
    def get_builder_config(self) -> str:
        """Getter to retrieve current builder configuration"""
        return "Registry: docker.io, Tag Prefix: v1.0"

    # ===== ADVANCED SERVICE PATTERNS =====

    @function
    async def create_http_service(self, port: int) -> dagger.Service:
        """Creates an HTTP service with health checks"""
        container = (
            dag.container()
            .from_("nginx:alpine")
            .with_exposed_port(port)
            .with_new_file("/usr/share/nginx/html/index.html", "<h1>Hello from Dagger Service!</h1>")
            .with_new_file("/usr/share/nginx/html/health", "OK")
        )
        return container.as_service()

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

    # ===== REMOTE REPOSITORY PATTERNS =====

    @function
    async def clone_and_build_remote(self, repo_url: str, branch: str) -> dagger.Container:
        """Clones a remote repository and builds it"""
        # Clone the repository
        source = dag.git(repo_url).branch(branch).tree()

        # Build the application (assuming it's a Go app)
        return (
            dag.container()
            .from_("golang:1.21")
            .with_mounted_directory("/src", source)
            .with_workdir("/src")
            .with_exec(["go", "mod", "download"])
            .with_exec(["go", "build", "-o", "/app", "."])
        )

    @function
    async def analyze_remote_repo(self, repo_url: str, file_pattern: str) -> str:
        """Analyzes files in a remote repository"""
        source = dag.git(repo_url).head().tree()

        return await (
            dag.container()
            .from_("alpine:latest")
            .with_mounted_directory("/repo", source)
            .with_workdir("/repo")
            .with_exec(["find", ".", "-name", file_pattern, "-type", "f", "-exec", "wc", "-l", "{}", ";"])
            .stdout()
        )

    # ===== MODULE DEPENDENCY PATTERNS =====

    @function
    async def use_remote_module(self, source: dagger.Directory, remote_module_ref: str) -> str:
        """Demonstrates using functions from remote modules"""
        # This would call functions from a remote module
        # For demo purposes, we'll simulate this
        return f"Would call functions from remote module: {remote_module_ref}\n\nExample: dagger -m {remote_module_ref} call some-function --source=. {source}"

    # ===== PACKAGE MANAGEMENT PATTERNS =====

    @function
    async def install_python_packages(self, requirements: list[str]) -> dagger.Container:
        """Installs Python packages in a container"""
        container = dag.container().from_("python:3.11-slim")

        # Create requirements.txt content
        req_content = "\n".join(requirements)
        req_file = dag.directory().with_new_file("requirements.txt", req_content).file("requirements.txt")

        return (
            container
            .with_file("/requirements.txt", req_file)
            .with_exec(["pip", "install", "-r", "/requirements.txt"])
        )

    @function
    async def build_with_dependencies(self, source: dagger.Directory, deps: list[str]) -> dagger.Container:
        """Builds an application with specified dependencies"""
        container = dag.container().from_("python:3.11-slim")

        # Install dependencies
        for dep in deps:
            container = container.with_exec(["pip", "install", dep])

        # Mount source and run
        return (
            container
            .with_mounted_directory("/app", source)
            .with_workdir("/app")
            .with_exec(["python", "main.py"])
        )
