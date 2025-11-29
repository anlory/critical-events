# Critical Event Log Reader

This tool reads and display Android critical event logs stored in protobuf format.

## Overview

The critical event log system in Android records important system events such as:
- Application Not Responding (ANR) errors
- System watchdog events
- Java and native crashes
- Excessive binder calls
- System server startup events
- Package installation events

These logs are stored in protobuf format as defined in [critical_event_log.proto](critical_event_log.proto).

## Installation

### With uv (recommended)

Install with [uv](https://docs.astral.sh/uv/):

```bash
uv tool install critical-events --editable
```

After installation, you can run the tool directly:

```bash
critical-events <protobuf_file>
```

### Manual installation

Install dependencies:

```bash
pip install protobuf
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv pip install protobuf
```

## Prerequisites

- Python 3.x
- Protocol Buffers library for Python:
  ```
  pip install protobuf
  ```
- Android Debug Bridge (adb) for automatic file pulling:
  ```
  # Usually comes with Android SDK platform tools
  ```

## Files

- [critical_event_log.proto](critical_event_log.proto) - The protobuf definition file
- [critical_event_log_pb2.py](critical_event_log_pb2.py) - The generated Python code from the protobuf definition
- [read_critical_events.py](read_critical_events.py) - The Python script to read and display protobuf files

## Usage

Once installed as a tool with uv, you can run the tool directly:

```bash
critical-events <protobuf_file>
```

You can also run it directly with Python:

```bash
python -m read_critical_events <protobuf_file>
```

### Basic Usage

```bash
critical-events <protobuf_file>
```

By default, the script assumes the file is in `CriticalEventLogStorageProto` format.

### Automatic File Pulling from Android Device

```bash
# Automatically pull and read from connected Android device
critical-events --auto
```

This will pull the file from the default location `/data/misc/critical-events/log.pb` on the connected Android device.

### Filtering by Event Types

```bash
# Show only specific event types
critical-events <protobuf_file> --event-types anr,java_crash

# Pull from device and show only watchdog events
critical-events --auto --event-types watchdog
```

Available event types:
- `watchdog`
- `half_watchdog`
- `anr`
- `java_crash`
- `native_crash`
- `system_server_started`
- `install_packages`
- `excessive_binder_calls`

### Debug Mode

To see raw file information:
```bash
critical-events <protobuf_file> debug
```

## Example Output

```
==================================================
CRITICAL EVENT STORAGE
==================================================
Events Count: 3
--------------------------------------------------
Event #1:
  Time: 2023-05-15 14:31:05.456 (1684157465456 ms)
  Type: App Not Responding (ANR)
    Subject: Broadcast of Intent { act=android.intent.action.TIME_TICK flg=0x50200014 cmp=com.android.systemui/.SystemUI }
    Process: com.android.systemui (PID: 1234, UID: 1000)
    Process Class: SYSTEM_SERVER

Event #2:
  Time: 2023-05-15 14:31:32.789 (1684157492789 ms)
  Type: Java Crash
    Exception: java.lang.NullPointerException
    Process: com.example.app (PID: 5678, UID: 10123)
    Process Class: DATA_APP
```

## Protobuf Message Types

### CriticalEventLogStorageProto (Only Supported Format)

This is the on-disk storage format containing only:
- `events`: List of critical events

### Critical Events

Each event contains:
- `timestamp_ms`: When the event occurred
- One of the following event types:
  - `watchdog`: System watchdog events
  - `half_watchdog`: Partial watchdog detection
  - `anr`: Application Not Responding
  - `java_crash`: Java application crashes
  - `native_crash`: Native process crashes
  - `system_server_started`: System server initialization
  - `install_packages`: Package installation events
  - `excessive_binder_calls`: High volume binder transactions

## Troubleshooting

If you encounter issues reading a file:
1. Verify the file is actually a protobuf file generated from the expected format
2. Ensure you're using the correct version of the protobuf definition
3. For `--auto` mode, make sure:
   - ADB is installed and in your PATH
   - An Android device is connected
   - You have proper permissions to access the file on the device

## License

This code is licensed under the same license as the Android Open Source Project.
See the LICENSE file for more information.