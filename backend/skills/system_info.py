import psutil
import platform
import datetime

def get_system_status() -> dict:
    """Return CPU, Memory, Disk, and Battery diagnostics."""
    battery = psutil.sensors_battery()
    battery_info = "Desktop / No battery"
    battery_percent = 100
    is_plugged = True
    
    if battery:
        battery_percent = round(battery.percent)
        is_plugged = battery.power_plugged
        status = "charging" if is_plugged else "discharging"
        battery_info = f"{battery_percent}% ({status})"

    cpu_usage = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')

    return {
        "os": f"{platform.system()} {platform.release()}",
        "cpu_percent": cpu_usage,
        "ram_percent": memory.percent,
        "ram_used_gb": round(memory.used / (1024**3), 1),
        "ram_total_gb": round(memory.total / (1024**3), 1),
        "disk_free_gb": round(disk.free / (1024**3), 1),
        "battery_percent": battery_percent,
        "battery_plugged": is_plugged,
        "battery_text": battery_info,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

def get_status_speech() -> str:
    status = get_system_status()
    return (
        f"Systems operational, {status['os']}. "
        f"CPU is running at {status['cpu_percent']} percent, "
        f"RAM usage is at {status['ram_percent']} percent, "
        f"and power levels stand at {status['battery_text']}."
    )
