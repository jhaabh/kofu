from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, List, Optional

class LocalThreadedExecutor:
    def __init__(self, tasks: List, memory, max_concurrency: int = 4, stop_all_when: Optional[Callable] = None):
        """
        Initialize the LocalThreadedExecutor.

        :param tasks: List of task instances that can be executed.
        :param memory: Memory object (e.g., SQLiteMemory) to manage task states and results.
        :param max_concurrency: Maximum number of threads to run concurrently.
        :param stop_all_when: Function that returns True if execution should stop (e.g., rate limiting, API blocks).
        """
        self.tasks = tasks
        self.memory = memory
        self.max_concurrency = max_concurrency
        self.stop_all_when = stop_all_when
        self._stopped = False

    def status_summary(self):
        """
        Print a summary of task statuses: pending, completed, failed.
        """
        pending = self.memory.get_pending_tasks()
        completed = self.memory.get_completed_tasks()
        failed = self.memory.get_failed_tasks()

        print(f"Pending tasks: {len(pending)}")
        print(f"Completed tasks: {len(completed)}")
        print(f"Failed tasks: {len(failed)}")

    def run(self):
        """
        Run the tasks concurrently with a thread pool. Query memory for task status to skip completed tasks
        and stop execution if the stop_all_when condition is met.
        """
        # Retrieve pending tasks from memory
        pending_task_ids = set(self.memory.get_pending_tasks())
        tasks_to_run = [task for task in self.tasks if task.get_id() in pending_task_ids]

        if not tasks_to_run:
            print("All tasks are already completed.")
            return

        # Thread pool execution
        with ThreadPoolExecutor(max_workers=self.max_concurrency) as executor:
            future_to_task = {executor.submit(self._execute_task, task): task for task in tasks_to_run}

            for future in as_completed(future_to_task):
                task = future_to_task[future]
                try:
                    result = future.result()  # This will raise an exception if the task failed
                    self.memory.update_task_statuses([(task.get_id(), 'completed', result, None)])
                except Exception as e:
                    self.memory.update_task_statuses([(task.get_id(), 'failed', None, str(e))])

                # Check if the stop condition is met (e.g., rate-limiting, API block)
                if self.stop_all_when and self.stop_all_when():
                    print(f"Emergency stop condition met. Halting execution.")
                    self._stopped = True
                    break

        # Print status summary at the end
        self.status_summary()

    def _execute_task(self, task):
        """
        Execute the given task and return its result.
        This function will be executed by each thread in the thread pool.
        """
        if self._stopped:
            raise RuntimeError("Execution was stopped by an external condition.")
        return task()

