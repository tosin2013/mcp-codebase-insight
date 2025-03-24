## Task Management API

The Task Management API provides endpoints for creating, listing, and retrieving information about asynchronous tasks.

### Create Task

**Endpoint:** `POST /api/tasks/create`

Create a new asynchronous task for processing.

**Request Body:**

```json
{
  "type": "code_analysis",
  "title": "Analyze Repository",
  "description": "Full code analysis of the repository",
  "context": {
    "repository_path": "/path/to/repo"
  },
  "priority": "medium",
  "metadata": {
    "requested_by": "user123"
  }
}
```

**Parameters:**

- `type` (string, required): Type of task to create (e.g., `code_analysis`, `pattern_extraction`, `documentation`)
- `title` (string, required): Title of the task
- `description` (string, required): Description of what the task will do
- `context` (object, required): Context data for the task, varies based on task type
- `priority` (string, optional): Task priority (`low`, `medium`, `high`, `critical`), defaults to `medium`
- `metadata` (object, optional): Additional metadata for the task

**Response:**

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "type": "code_analysis",
  "title": "Analyze Repository",
  "description": "Full code analysis of the repository",
  "status": "pending",
  "priority": "medium",
  "context": {
    "repository_path": "/path/to/repo"
  },
  "result": null,
  "error": null,
  "created_at": "2023-07-10T14:30:00.123456",
  "updated_at": "2023-07-10T14:30:00.123456",
  "completed_at": null,
  "metadata": {
    "requested_by": "user123"
  }
}
```

### List Tasks

**Endpoint:** `GET /api/tasks`

List all tasks with optional filtering.

**Query Parameters:**

- `type` (string, optional): Filter tasks by type
- `status` (string, optional): Filter tasks by status (`pending`, `in_progress`, `completed`, `failed`, `cancelled`)
- `priority` (string, optional): Filter tasks by priority
- `limit` (integer, optional): Maximum number of tasks to return, defaults to 20

**Response:**

```json
[
  {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "type": "code_analysis",
    "title": "Analyze Repository",
    "description": "Full code analysis of the repository",
    "status": "completed",
    "priority": "medium",
    "context": {
      "repository_path": "/path/to/repo"
    },
    "result": {
      "files_analyzed": 150,
      "patterns_identified": 5,
      "complexity_score": 78
    },
    "error": null,
    "created_at": "2023-07-10T14:30:00.123456",
    "updated_at": "2023-07-10T14:35:20.123456",
    "completed_at": "2023-07-10T14:35:20.123456",
    "metadata": {
      "requested_by": "user123"
    }
  },
  {
    "id": "223e4567-e89b-12d3-a456-426614174000",
    "type": "pattern_extraction",
    "title": "Extract Design Patterns",
    "description": "Identify design patterns in codebase",
    "status": "in_progress",
    "priority": "high",
    "context": {
      "repository_path": "/path/to/repo"
    },
    "result": null,
    "error": null,
    "created_at": "2023-07-10T14:40:00.123456",
    "updated_at": "2023-07-10T14:40:30.123456",
    "completed_at": null,
    "metadata": {
      "requested_by": "user456"
    }
  }
]
```

### Get Task by ID

**Endpoint:** `GET /api/tasks/{task_id}`

Get detailed information about a specific task.

**Path Parameters:**

- `task_id` (string, required): The unique identifier of the task

**Response:**

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "type": "code_analysis",
  "title": "Analyze Repository",
  "description": "Full code analysis of the repository",
  "status": "completed",
  "priority": "medium",
  "context": {
    "repository_path": "/path/to/repo"
  },
  "result": {
    "files_analyzed": 150,
    "patterns_identified": 5,
    "complexity_score": 78
  },
  "error": null,
  "created_at": "2023-07-10T14:30:00.123456",
  "updated_at": "2023-07-10T14:35:20.123456",
  "completed_at": "2023-07-10T14:35:20.123456",
  "metadata": {
    "requested_by": "user123"
  }
}
```

**Error Responses:**

- `400 Bad Request`: Invalid task ID format
- `404 Not Found`: Task not found
- `500 Internal Server Error`: Server error while retrieving task

## Debug System API

The Debug System API provides endpoints for creating, listing, and managing issues for debugging and tracking purposes.

### Create Debug Issue

**Endpoint:** `POST /api/debug/issues`

Create a new debug issue for tracking and analysis.

**Request Body:**

```json
{
  "title": "Memory Leak in Data Processing",
  "type": "performance",
  "description": {
    "severity": "high",
    "steps_to_reproduce": ["Load large dataset", "Run processing function", "Wait 10 minutes"],
    "expected_behavior": "Memory usage should remain stable",
    "actual_behavior": "Memory usage increases continuously"
  }
}
```

**Parameters:**

- `title` (string, required): Title of the issue
- `type` (string, required): Type of the issue - one of: `bug`, `performance`, `security`, `design`, `documentation`, `other`
- `description` (object, required): Detailed description of the issue, structure depends on issue type

**Response:**

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "title": "Memory Leak in Data Processing",
  "type": "performance",
  "status": "open",
  "description": {
    "severity": "high",
    "steps_to_reproduce": ["Load large dataset", "Run processing function", "Wait 10 minutes"],
    "expected_behavior": "Memory usage should remain stable",
    "actual_behavior": "Memory usage increases continuously"
  },
  "steps": null,
  "created_at": "2023-07-10T14:30:00.123456",
  "updated_at": "2023-07-10T14:30:00.123456",
  "resolved_at": null,
  "metadata": null
}
```

### List Debug Issues

**Endpoint:** `GET /api/debug/issues`

List all debug issues with optional filtering.

**Query Parameters:**

- `type` (string, optional): Filter issues by type
- `status` (string, optional): Filter issues by status (`open`, `in_progress`, `resolved`, `closed`, `wont_fix`)

**Response:**

```json
[
  {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "title": "Memory Leak in Data Processing",
    "type": "performance",
    "status": "open",
    "description": {
      "severity": "high",
      "steps_to_reproduce": ["Load large dataset", "Run processing function", "Wait 10 minutes"],
      "expected_behavior": "Memory usage should remain stable",
      "actual_behavior": "Memory usage increases continuously"
    },
    "steps": [
      {
        "type": "check",
        "name": "Profiling",
        "description": "Run performance profiling"
      },
      {
        "type": "check",
        "name": "Resource Usage",
        "description": "Monitor CPU, memory, I/O"
      }
    ],
    "created_at": "2023-07-10T14:30:00.123456",
    "updated_at": "2023-07-10T14:35:00.123456",
    "resolved_at": null,
    "metadata": {
      "assigned_to": "developer1"
    }
  }
]
```

### Get Debug Issue

**Endpoint:** `GET /api/debug/issues/{issue_id}`

Get detailed information about a specific debug issue.

**Path Parameters:**

- `issue_id` (string, required): The unique identifier of the issue

**Response:**

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "title": "Memory Leak in Data Processing",
  "type": "performance",
  "status": "open",
  "description": {
    "severity": "high",
    "steps_to_reproduce": ["Load large dataset", "Run processing function", "Wait 10 minutes"],
    "expected_behavior": "Memory usage should remain stable",
    "actual_behavior": "Memory usage increases continuously"
  },
  "steps": [
    {
      "type": "check",
      "name": "Profiling",
      "description": "Run performance profiling"
    },
    {
      "type": "check",
      "name": "Resource Usage",
      "description": "Monitor CPU, memory, I/O"
    }
  ],
  "created_at": "2023-07-10T14:30:00.123456",
  "updated_at": "2023-07-10T14:35:00.123456",
  "resolved_at": null,
  "metadata": {
    "assigned_to": "developer1"
  }
}
```

### Update Debug Issue

**Endpoint:** `PUT /api/debug/issues/{issue_id}`

Update the status and metadata of a debug issue.

**Path Parameters:**

- `issue_id` (string, required): The unique identifier of the issue

**Request Body:**

```json
{
  "status": "in_progress",
  "metadata": {
    "assigned_to": "developer1",
    "priority": "high"
  }
}
```

**Parameters:**

- `status` (string, optional): New status for the issue - one of: `open`, `in_progress`, `resolved`, `closed`, `wont_fix`
- `metadata` (object, optional): Updated metadata for the issue

**Response:**

Same as the Get Debug Issue response, with updated values.

### Analyze Debug Issue

**Endpoint:** `POST /api/debug/issues/{issue_id}/analyze`

Analyze a debug issue to generate recommended debugging steps based on the issue type.

**Path Parameters:**

- `issue_id` (string, required): The unique identifier of the issue

**Response:**

```json
[
  {
    "type": "check",
    "name": "Profiling",
    "description": "Run performance profiling"
  },
  {
    "type": "check",
    "name": "Resource Usage",
    "description": "Monitor CPU, memory, I/O"
  },
  {
    "type": "check",
    "name": "Query Analysis",
    "description": "Review database queries"
  },
  {
    "type": "check",
    "name": "Bottlenecks",
    "description": "Identify performance bottlenecks"
  }
]
```

**Error Responses:**

- `400 Bad Request`: Invalid issue ID format
- `404 Not Found`: Issue not found
- `500 Internal Server Error`: Server error during analysis 