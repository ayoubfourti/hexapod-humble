#!/usr/bin/env python3
# jetson_monitor.py — publie CPU / GPU / température de la Jetson Nano

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import json, psutil, re

def get_gpu_and_temp() -> dict:
    """Lit le fichier tegrastats écrit par l'hôte Jetson."""
    try:
        with open("/hexapod-humble/tegrastats.txt", "r") as f:
            line = f.read()

        gpu_match  = re.search(r'GR3D_FREQ\s+(\d+)%', line)
        temp_match = re.search(r'GPU@([\d.]+)C', line)

        return {
            "gpu":  float(gpu_match.group(1))  if gpu_match  else 0.0,
            "temp": float(temp_match.group(1)) if temp_match else 0.0,
        }
    except Exception:
        return {"gpu": 0.0, "temp": 0.0}

class JetsonMonitorNode(Node):
    def __init__(self):
        super().__init__("jetson_monitor")
        self.pub = self.create_publisher(String, "/jetson/system_stats", 10)
        self.create_timer(2.0, self.publish_stats)
        self.get_logger().info("✅ Jetson Monitor démarré")

    def publish_stats(self):
        hw = get_gpu_and_temp()
        stats = {
            "cpu":         round(psutil.cpu_percent(interval=0.5), 1),
            "gpu":         hw["gpu"],
            "temperature": hw["temp"],
            "battery":     100.0,
        }
        msg = String()
        msg.data = json.dumps(stats)
        self.pub.publish(msg)
        self.get_logger().info(f"📡 Stats: {stats}")

def main(args=None):
    rclpy.init(args=args)
    node = JetsonMonitorNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()
