#!/usr/bin/env python3

"""
Script to read and display critical event logs stored in protobuf format.
"""

import sys
import os
import subprocess
import tempfile
import critical_event_log.critical_event_log_pb2 as critical_event_log_pb2


def format_timestamp(timestamp_ms):
    """Convert timestamp in milliseconds to readable format"""
    from datetime import datetime
    # Handle case where timestamp might be 0 or invalid
    if timestamp_ms <= 0:
        return "Invalid timestamp"
    try:
        return datetime.fromtimestamp(timestamp_ms / 1000).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    except:
        return f"Invalid timestamp: {timestamp_ms}"


def display_event(event):
    """Display a critical event in human-readable format"""
    print(f"  Time: {format_timestamp(event.timestamp_ms)} ({event.timestamp_ms} ms)")
    
    # Check which event type is present
    event_type = event.WhichOneof('event')
    if event_type == 'watchdog':
        print("  Type: Watchdog")
        print(f"    Subject: {event.watchdog.subject}")
        print(f"    UUID: {event.watchdog.uuid}")
        
    elif event_type == 'half_watchdog':
        print("  Type: Half Watchdog")
        print(f"    Subject: {event.half_watchdog.subject}")
        
    elif event_type == 'anr':
        print("  Type: App Not Responding (ANR)")
        print(f"    Subject: {event.anr.subject or 'N/A'}")
        print(f"    Process: {event.anr.process or 'N/A'}")
        print(f"    PID: {event.anr.pid}")
        print(f"    UID: {event.anr.uid}")
        process_class_name = critical_event_log_pb2.CriticalEventProto.ProcessClass.Name(event.anr.process_class)
        print(f"    Process Class: {process_class_name}")
        
    elif event_type == 'java_crash':
        print("  Type: Java Crash")
        print(f"    Exception: {event.java_crash.exception_class or 'N/A'}")
        print(f"    Process: {event.java_crash.process or 'N/A'}")
        print(f"    PID: {event.java_crash.pid}")
        print(f"    UID: {event.java_crash.uid}")
        process_class_name = critical_event_log_pb2.CriticalEventProto.ProcessClass.Name(event.java_crash.process_class)
        print(f"    Process Class: {process_class_name}")
        
    elif event_type == 'native_crash':
        print("  Type: Native Crash")
        print(f"    Process: {event.native_crash.process or 'N/A'}")
        print(f"    PID: {event.native_crash.pid}")
        print(f"    UID: {event.native_crash.uid}")
        process_class_name = critical_event_log_pb2.CriticalEventProto.ProcessClass.Name(event.native_crash.process_class)
        print(f"    Process Class: {process_class_name}")
        
    elif event_type == 'system_server_started':
        print("  Type: System Server Started")
        
    elif event_type == 'install_packages':
        print("  Type: Install Packages")
        
    elif event_type == 'excessive_binder_calls':
        print("  Type: Excessive Binder Calls")
        print(f"    UID: {event.excessive_binder_calls.uid}")
        
    else:
        print(f"  Type: Unknown ({event_type})")
    
    return event_type


def read_critical_event_storage(filename, event_filters=None):
    """Read and display critical event storage from protobuf file"""
    # Create a CriticalEventLogStorageProto message
    storage = critical_event_log_pb2.CriticalEventLogStorageProto()
    
    # Read the file
    try:
        with open(filename, 'rb') as f:
            data = f.read()
            print(f"Reading {len(data)} bytes from {filename}")
            storage.ParseFromString(data)
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return 1
    except Exception as e:
        print(f"Error reading file: {e}")
        return 1
    
    # Display storage info
    print("=" * 50)
    print("CRITICAL EVENT STORAGE")
    print("=" * 50)
    print(f"Events Count: {len(storage.events)}")
    print("-" * 50)
    
    # Display each event
    if len(storage.events) == 0:
        print("No events found in storage.")
    else:
        displayed_count = 0
        for i, event in enumerate(storage.events):
            event_type = event.WhichOneof('event')
            # 如果指定了过滤器，则只显示匹配的事件类型
            if event_filters and event_type not in event_filters:
                continue
                
            print(f"Event #{i+1}:")
            display_event(event)
            print()
            displayed_count += 1
            
        if event_filters and displayed_count == 0:
            print(f"No events of type(s) {', '.join(event_filters)} found.")
    
    return 0


def pull_from_android_device(remote_path="/data/misc/critical-events/critical_event_log.pb"):
    """Pull critical events log from Android device"""
    try:
        # 创建临时文件来存储拉取的内容
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file.close()
        
        # 构建adb命令，不指定设备ID
        cmd = ["adb", "pull", remote_path, temp_file.name]
        
        print(f"Executing: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Error pulling file from device: {result.stderr}")
            # 清理临时文件
            os.unlink(temp_file.name)
            return None
            
        print(f"Successfully pulled {remote_path} from device to {temp_file.name}")
        return temp_file.name
    except Exception as e:
        print(f"Error executing adb command: {e}")
        return None


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  {} <protobuf_file> [--event-types TYPE1,TYPE2,...]".format(sys.argv[0]))
        print("  {} --auto [--event-types TYPE1,TYPE2,...]".format(sys.argv[0]))
        print()
        print("Examples:")
        print("  {} critical_events.pb  # Read protobuf file".format(sys.argv[0]))
        print("  {} critical_events.pb --event-types [system_server_started,anr,java_crash,native_crash,watchdog,half_watchdog,install_packages,excessive_binder_calls]  # Only show ANR and Java crash events".format(sys.argv[0]))
        print("  {} --auto  # Pull from device and read".format(sys.argv[0]))
        print("  {} --auto --event-types watchdog  # Pull from device and show only watchdog events".format(sys.argv[0]))
        return 1
    
    # 解析参数
    args = sys.argv[1:]
    auto_mode = False
    event_filters = None
    filename = None
    
    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "--auto":
            auto_mode = True
        elif arg == "--event-types":
            if i + 1 < len(args):
                event_filters = args[i + 1].split(",")
                i += 1  # Skip the next argument
            else:
                print("Error: --event-types requires a comma-separated list of event types")
                return 1
        elif arg.startswith("--"):  # Other unrecognized flag
            print(f"Error: Unrecognized option {arg}")
            return 1
        else:
            # Positional arguments
            if not filename and not auto_mode:
                filename = arg
            else:
                print(f"Error: Unexpected argument {arg}")
                return 1
        i += 1
    
    # 验证参数组合
    if auto_mode:
        # 在auto模式下，我们需要从设备拉取文件
        remote_path = "/data/misc/critical-events/critical_event_log.pb"
        print("Pulling critical events log from Android device...")
        local_file = pull_from_android_device(remote_path)
        
        if not local_file:
            return 1
            
        filename = local_file
    elif not filename:
        print("Error: No input file specified")
        return 1
    
    # 执行读取操作（默认且唯一格式为storage）
    result = 0
    try:
        result = read_critical_event_storage(filename, event_filters)
    finally:
        # 如果是从设备拉取的临时文件，清理它
        if auto_mode and filename and os.path.exists(filename):
            try:
                os.unlink(filename)
                print(f"Cleaned up temporary file: {filename}")
            except Exception as e:
                print(f"Warning: Failed to clean up temporary file {filename}: {e}")
    
    return result


if __name__ == "__main__":
    sys.exit(main())