#!/usr/bin/env python3
import argparse
import json
import os
import sys

DEFAULT_FILENAME = "tasks.json"

def load_tasks(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Expecting list of tasks: each is dict with "id", "desc", "completed"
            if isinstance(data, list):
                return data
            else:
                return []
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        print(f"Error: Could not parse JSON in {filename}. Starting with empty task list.", file=sys.stderr)
        return []

def save_tasks(filename, tasks):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=2)

def get_next_id(tasks):
    if not tasks:
        return 1
    else:
        # find max existing id
        max_id = max(task.get("id", 0) for task in tasks)
        return max_id + 1

def cmd_add(args):
    filename = args.file or os.getenv("TODO_FILE") or DEFAULT_FILENAME
    tasks = load_tasks(filename)
    new_id = get_next_id(tasks)
    task = {"id": new_id, "desc": args.description, "completed": False}
    tasks.append(task)
    save_tasks(filename, tasks)
    print(f"Added task {new_id}: {args.description}")

def cmd_list(args):
    filename = args.file or os.getenv("TODO_FILE") or DEFAULT_FILENAME
    tasks = load_tasks(filename)
    if not tasks:
        print("No tasks found.")
        return
    for task in tasks:
        status = "✓" if task.get("completed") else " "
        print(f"[{status}] {task.get('id')}: {task.get('desc')}")

def cmd_complete(args):
    filename = args.file or os.getenv("TODO_FILE") or DEFAULT_FILENAME
    tasks = load_tasks(filename)
    for task in tasks:
        if task.get("id") == args.id:
            if task.get("completed"):
                print(f"Task {args.id} is already completed.")
            else:
                task["completed"] = True
                save_tasks(filename, tasks)
                print(f"Marked task {args.id} as completed.")
            return
    print(f"Task {args.id} not found.", file=sys.stderr)
    sys.exit(1)

def cmd_remove(args):
    filename = args.file or os.getenv("TODO_FILE") or DEFAULT_FILENAME
    tasks = load_tasks(filename)
    new_tasks = [task for task in tasks if task.get("id") != args.id]
    if len(new_tasks) == len(tasks):
        print(f"Task {args.id} not found.", file=sys.stderr)
        sys.exit(1)
    save_tasks(filename, new_tasks)
    print(f"Removed task {args.id}.")

def main():
    parser = argparse.ArgumentParser(prog="todo", description="Simple TODO CLI")
    # Global option to override file (for tests or explicit use)
    parser.add_argument("--file", help="Path to tasks JSON file (default: tasks.json in current directory)")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # add
    p_add = subparsers.add_parser("add", help="Add a new task")
    p_add.add_argument("description", help="Task description, wrap in quotes if spaces")
    p_add.set_defaults(func=cmd_add)

    # list
    p_list = subparsers.add_parser("list", help="List all tasks")
    p_list.set_defaults(func=cmd_list)

    # complete
    p_complete = subparsers.add_parser("complete", help="Mark a task as completed")
    p_complete.add_argument("id", type=int, help="ID of task to complete")
    p_complete.set_defaults(func=cmd_complete)

    # remove
    p_remove = subparsers.add_parser("remove", help="Remove a task")
    p_remove.add_argument("id", type=int, help="ID of task to remove")
    p_remove.set_defaults(func=cmd_remove)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
