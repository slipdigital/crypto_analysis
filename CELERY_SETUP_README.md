# Celery Integration for Crypto Dashboard

This document describes the Celery integration for the Flask Crypto Dashboard, providing robust background task processing capabilities.

## 🏗️ Architecture Overview

The Celery integration replaces the previous threading-based background tasks with a more scalable and reliable distributed task queue system.

### Components

1. **Flask Application** (`app.py`) - Web interface with Celery task endpoints
2. **Celery Configuration** (`celery_config.py`) - Celery app configuration
3. **Task Definitions** (`tasks.py`) - Background task implementations
4. **Worker Process** (`celery_worker.py`) - Task execution workers
5. **Management Tools** (`celery_manager.py`) - Monitoring and management utilities
6. **Redis Broker** - Message broker for task queuing

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start Redis Server

**Windows (using Redis for Windows):**
```bash
redis-server
```

**macOS (using Homebrew):**
```bash
brew services start redis
```

**Linux:**
```bash
sudo systemctl start redis
```

### 3. Start Celery Worker

```bash
python celery_worker.py
```

**Or using the management script:**
```bash
python celery_manager.py worker
```

### 4. Start Flask Application

```bash
python app.py
```

### 5. Access the Dashboard

Open your browser to: `http://localhost:5000`

## 📋 Available Tasks

### Background Tasks

1. **`run_crypto_backtest`** - Execute cryptocurrency backtesting analysis
2. **`run_data_collection`** - Collect fresh cryptocurrency data
3. **`generate_reports`** - Generate market cap and performance reports
4. **`cleanup_old_results`** - Clean up old files and task results
5. **`health_check`** - Worker health monitoring

### Dashboard Controls

The dashboard now includes three main action buttons:

- **🟢 Run Backtest** - Execute backtesting analysis
- **🔵 Collect Data** - Fetch latest cryptocurrency data
- **🟡 Generate Reports** - Create market cap and performance reports

## 🔧 Management Commands

### Celery Manager CLI

```bash
# Start worker with custom settings
python celery_manager.py worker --concurrency 4 --loglevel debug

# Start beat scheduler for periodic tasks
python celery_manager.py beat

# Monitor active tasks in real-time
python celery_manager.py monitor

# Show worker statistics
python celery_manager.py stats

# Purge all tasks from queues
python celery_manager.py purge
```

### Direct Celery Commands

```bash
# Start worker directly
celery -A celery_config.celery_app worker --loglevel=info

# Start beat scheduler
celery -A celery_config.celery_app beat --loglevel=info

# Monitor tasks
celery -A celery_config.celery_app flower
```

## 🎯 Task Configuration

### Worker Settings

| Setting | Default | Description |
|---------|---------|-------------|
| Concurrency | 2 | Number of worker processes |
| Queue | crypto_tasks | Task queue name |
| Loglevel | info | Logging verbosity |
| Pool | prefork | Worker pool type |

### Task Timeouts

| Task | Soft Limit | Hard Limit |
|------|------------|------------|
| Backtest | 25 minutes | 30 minutes |
| Data Collection | 15 minutes | 20 minutes |
| Report Generation | 8 minutes | 10 minutes |

### Retry Policy

- **Max Retries**: 3
- **Retry Delay**: 60 seconds
- **Exponential Backoff**: Enabled

## 📊 Monitoring & Status

### Dashboard Task Monitor

The dashboard includes a real-time task monitoring section showing:

- Task ID and name
- Current status (Pending, Running, Completed, Failed)
- Progress percentage
- Worker assignment
- Action buttons (Cancel, View Results)

### Task States

| State | Description | Actions Available |
|-------|-------------|-------------------|
| PENDING | Task queued, waiting for worker | Cancel |
| PROGRESS | Task currently executing | Cancel, Monitor |
| SUCCESS | Task completed successfully | View Results |
| FAILURE | Task failed with error | View Error |
| REVOKED | Task cancelled by user | None |

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/run-backtest` | POST | Start backtest task |
| `/api/run-data-collection` | POST | Start data collection |
| `/api/generate-reports` | POST | Start report generation |
| `/api/task-status/<id>` | GET | Get task status |
| `/api/tasks` | GET | List active tasks |
| `/api/cancel-task/<id>` | POST | Cancel task |

## 🔗 Integration with Existing System

### Data Sources

The Celery tasks integrate seamlessly with existing components:

- **Backtest Tasks** → `backtest/crypto_backtest.py`
- **Data Collection** → `backtest/crypto_collector.py`
- **Market Reports** → `market_cap/market_cap_report.py`
- **Performance Reports** → `crypto_performance/performance_report.py`

### File Structure

```
crypto_analysis/
├── app.py                    # Flask app with Celery integration
├── celery_config.py          # Celery configuration
├── tasks.py                  # Task definitions
├── celery_worker.py          # Worker startup script
├── celery_manager.py         # Management CLI
├── requirements.txt          # Updated with Celery dependencies
└── templates/
    └── dashboard.html        # Updated with task controls
```

## 🛠️ Configuration

### Redis Configuration

**Default Connection:**
```python
redis://localhost:6379/0
```

**Custom Redis URL:**
```bash
export REDIS_URL="redis://your-redis-server:6379/0"
```

### Celery Settings

Edit `celery_config.py` to customize:

```python
# Task routing
task_routes={
    'tasks.run_crypto_backtest': {'queue': 'crypto_tasks'},
    'tasks.run_data_collection': {'queue': 'crypto_tasks'},
}

# Worker settings
worker_prefetch_multiplier=1
task_acks_late=True

# Task timeouts
task_time_limit=30 * 60  # 30 minutes
task_soft_time_limit=25 * 60  # 25 minutes
```

### Periodic Tasks

The system supports scheduled tasks via Celery Beat:

```python
beat_schedule={
    'daily-data-collection': {
        'task': 'tasks.run_data_collection',
        'schedule': timedelta(hours=24),
    },
    'hourly-market-reports': {
        'task': 'tasks.generate_reports',
        'schedule': timedelta(hours=1),
    },
}
```

## 🚨 Troubleshooting

### Common Issues

1. **Redis Connection Error**
   ```
   Error: [Errno 61] Connection refused
   ```
   **Solution:** Start Redis server before starting workers

2. **Task Never Starts**
   ```
   Task status remains PENDING
   ```
   **Solution:** Ensure workers are running and connected

3. **Import Errors**
   ```
   ModuleNotFoundError: No module named 'tasks'
   ```
   **Solution:** Run from project root directory

4. **Worker Crashes**
   ```
   Worker terminated unexpectedly
   ```
   **Solution:** Check worker logs and task dependencies

### Debugging Commands

```bash
# Check Redis connectivity
redis-cli ping

# List active workers
celery -A celery_config.celery_app inspect active

# Show registered tasks
celery -A celery_config.celery_app inspect registered

# Monitor task execution
celery -A celery_config.celery_app events

# Clear all tasks
celery -A celery_config.celery_app purge
```

### Log Locations

- **Worker Logs**: Console output with timestamps
- **Task Logs**: Integrated with application logging
- **Redis Logs**: Redis server logs (location varies by system)

## 📈 Performance Optimization

### Scaling Workers

```bash
# Multiple workers on single machine
python celery_manager.py worker --concurrency 4

# Multiple worker processes
python celery_worker.py &
python celery_worker.py &
```

### Memory Management

- Workers automatically restart after 1000 tasks
- Task results expire after 1 hour
- Failed task cleanup runs daily

### Network Optimization

- Redis connection pooling enabled
- Task compression for large payloads
- Optimized serialization (JSON)

## 🔒 Security Considerations

### Production Deployment

1. **Redis Security**
   - Enable Redis authentication
   - Use Redis over SSL/TLS
   - Configure firewall rules

2. **Task Security**
   - Validate task inputs
   - Sanitize file paths
   - Limit task execution time

3. **Network Security**
   - Use private networks for Redis
   - Enable broker SSL
   - Monitor task queues

### Configuration Example

```python
# Production Celery config
celery_app.conf.update(
    broker_use_ssl=True,
    redis_backend_use_ssl=True,
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    result_expires=3600,
    worker_log_level='WARNING'
)
```

## 🎉 Benefits of Celery Integration

### Reliability
- ✅ Task persistence across restarts
- ✅ Automatic retry on failure
- ✅ Dead letter queues for failed tasks
- ✅ Worker health monitoring

### Scalability
- ✅ Horizontal scaling across multiple machines
- ✅ Queue-based load balancing
- ✅ Resource isolation per task type
- ✅ Auto-scaling workers

### Monitoring
- ✅ Real-time task status
- ✅ Performance metrics
- ✅ Error tracking and alerting
- ✅ Historical task data

### User Experience
- ✅ Non-blocking web interface
- ✅ Progress tracking
- ✅ Task cancellation
- ✅ Result visualization

---

**For additional support or questions about the Celery integration, refer to the [Celery Documentation](https://docs.celeryproject.org/) or check the application logs.**