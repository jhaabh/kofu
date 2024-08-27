# Messor

**Messor** (Latin for "Harvester") is a Python framework for managing and executing tasks with concurrency and persistence. It’s designed to handle I/O-heavy operations such as web scraping, LLM-based workflows, or any task that requires data collection across multiple steps or executions. 

## Features

- **Local Threaded Execution**: Run tasks concurrently with Python threads.
- **Task Resumption**: Automatically resume pending or failed tasks after interruptions or crashes.
- **Memory Persistence**: Store task statuses and results in various backends like SQLite or custom memory systems.
- **Stop Conditions**: Gracefully stop execution based on custom conditions (e.g., rate-limiting, API blocks).
- **Task Retry**: Automatically retry tasks that fail up to a configurable number of attempts.
- **Error Handling**: Capture and handle task execution errors, store error details, and retry tasks if needed.

## Installation

You can install **Messor** via pip after it’s been published to PyPI.

```bash
pip install messor
```

## Basic Usage

Below is a simple example of how to use the `LocalThreadedExecutor` and `SQLiteMemory` to manage and execute tasks concurrently.

### 1. Define Tasks
Each task needs to have a `get_id()` method to uniquely identify it and a `__call__()` method to execute the task logic.

```python
# Define your tasks
class ExampleTask:
    def __init__(self, task_id, url):
        self.task_id = task_id
        self.url = url

    def get_id(self):
        return self.task_id

    def __call__(self):
        # Simulate task execution
        return f"Processed {self.url}"
```

### 2. Set up Memory for Task Persistence
The memory stores task definitions, statuses, results, and errors. You can use `SQLiteMemory` to persist data to an SQLite database.

```python
from messor.sqlite_memory import SQLiteMemory

# Set up SQLite memory for task persistence
memory = SQLiteMemory(path="tasks.db")
```

### 3. Run the Executor
Use the `LocalThreadedExecutor` to manage the execution of tasks with concurrency. You can configure the maximum concurrency level, stop conditions, and task retry behavior.

```python
from messor.local_threaded_executor import LocalThreadedExecutor

# Define a list of tasks
tasks = [
    ExampleTask("task_1", "http://example.com"),
    ExampleTask("task_2", "http://example.org"),
    ExampleTask("task_3", "http://example.net"),
]

# Initialize the executor with task memory and run it
executor = LocalThreadedExecutor(tasks=tasks, memory=memory, max_concurrency=2, retry=2)
executor.run()
```

### 4. Status Reporting
You can query the task statuses during or after execution to see which tasks are pending, completed, or failed.

```python
executor.status_summary()
```

### 5. Handling Failures and Resumption
Messor automatically handles task failures by storing error information in memory. When the executor is run again, it will skip tasks marked as completed and retry those marked as failed or pending.

```python
# Re-run the executor to resume any pending or failed tasks
executor.run()
```

## Advanced Features

### Stop Conditions
You can define custom stop conditions for halting execution based on external events (e.g., rate limits, API blocks). The stop condition is checked after each task is completed, but tasks that have already started will continue to run.

```python
# Stop condition that halts execution after two tasks are processed
executed_tasks = 0
def stop_after_two_tasks():
    global executed_tasks
    return executed_tasks >= 2

class ExampleTaskWithCount(ExampleTask):
    def __call__(self):
        global executed_tasks
        executed_tasks += 1
        return super().__call__()

# Use the stop condition in the executor
executor = LocalThreadedExecutor(tasks=tasks, memory=memory, max_concurrency=2, stop_all_when=stop_after_two_tasks)
executor.run()
```

### Custom Memory Backends
You can create custom memory backends by implementing the `Memory` interface, allowing you to store task data in other systems like Firebase, AWS S3, etc.

```python
class CustomMemory:
    def store_tasks(self, tasks):
        # Custom storage logic
        pass

    def update_task_statuses(self, statuses):
        # Custom status update logic
        pass

    def get_task_status(self, task_id):
        # Retrieve task status
        pass

    def get_completed_tasks(self):
        # Retrieve completed tasks
        pass

# Use CustomMemory in the executor
custom_memory = CustomMemory()
executor = LocalThreadedExecutor(tasks=tasks, memory=custom_memory, max_concurrency=4)
executor.run()
```

## Running Tests

To run the test suite, install the necessary dependencies and run pytest:

```bash
pip install pytest
pytest
```

The test suite is divided into multiple files that focus on specific parts of the framework, including task execution, concurrency, resumption, and error handling.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue to report bugs or request features.

### Development Setup

1. Clone the repository:

```bash
git clone https://github.com/yourusername/messor.git
cd messor
```

2. Create a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows use: .\venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Run tests to ensure everything is working:

```bash
pytest
```

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

---

Happy Harvesting with **Messor**! 🌾