import os
import sys
import subprocess
import tempfile
import unittest

# Path to todo.py in project root
SCRIPT = os.path.join(os.path.dirname(__file__), os.pardir, "todo.py")

class TodoCLITest(unittest.TestCase):
    def run_cmd(self, args, env=None):
        """
        Run todo.py with given args list, return (exitcode, stdout, stderr)
        """
        cmd = [sys.executable, SCRIPT] + args
        # Use a copy of env or None
        result = subprocess.run(cmd, capture_output=True, text=True, env=env)
        return result.returncode, result.stdout.strip(), result.stderr.strip()

    def setUp(self):
        # Create a temporary file for tasks, starting empty
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        tmp.write(b"[]")
        tmp.flush()
        tmp.close()
        self.tasks_file = tmp.name

    def tearDown(self):
        try:
            os.remove(self.tasks_file)
        except OSError:
            pass

    def test_add_and_list(self):
        code, out, err = self.run_cmd(["--file", self.tasks_file, "add", "Test task"])
        self.assertEqual(code, 0)
        self.assertIn("Added task 1: Test task", out)

        code, out, err = self.run_cmd(["--file", self.tasks_file, "list"])
        self.assertEqual(code, 0)
        self.assertIn("[ ] 1: Test task", out)

    def test_complete(self):
        # Add two tasks
        self.run_cmd(["--file", self.tasks_file, "add", "First"])
        self.run_cmd(["--file", self.tasks_file, "add", "Second"])
        # Complete task 1
        code, out, err = self.run_cmd(["--file", self.tasks_file, "complete", "1"])
        self.assertEqual(code, 0)
        self.assertIn("Marked task 1 as completed.", out)

        code, out, err = self.run_cmd(["--file", self.tasks_file, "list"])
        self.assertIn("[✓] 1: First", out)
        self.assertIn("[ ] 2: Second", out)

    def test_remove(self):
        # Add and then remove
        self.run_cmd(["--file", self.tasks_file, "add", "ToRemove"])
        code, out, err = self.run_cmd(["--file", self.tasks_file, "remove", "1"])
        self.assertEqual(code, 0)
        self.assertIn("Removed task 1.", out)

        code, out, err = self.run_cmd(["--file", self.tasks_file, "list"])
        self.assertIn("No tasks found.", out)

    def test_complete_nonexistent(self):
        code, out, err = self.run_cmd(["--file", self.tasks_file, "complete", "5"])
        self.assertNotEqual(code, 0)
        self.assertIn("Task 5 not found.", err)

    def test_remove_nonexistent(self):
        code, out, err = self.run_cmd(["--file", self.tasks_file, "remove", "10"])
        self.assertNotEqual(code, 0)
        self.assertIn("Task 10 not found.", err)

if __name__ == "__main__":
    unittest.main()
