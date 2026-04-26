#!/usr/bin/env python3
# serial_bridge.py
import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Float32MultiArray
import serial
import threading
import time

SERIAL_PORT  = "/dev/ttyUSB0"
BAUD_RATE    = 9600
MIN_INTERVAL = 0.1

class SerialBridge(Node):
    def __init__(self):
        super().__init__("serial_bridge")

        try:
            self.ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
            self.get_logger().info(f"Arduino connecté sur {SERIAL_PORT}")
        except Exception as e:
            self.get_logger().error(f"Erreur port série: {e}")
            self.ser = None

        self._last_sent_time = 0.0
        self._last_cmd = None

        # ── Publishers ─────────────────────────────────────────────────────────
        self.sub = self.create_subscription(
            String, "/cmd_serial", self.cmd_callback, 10
        )

        # ★ NOUVEAU : topic IMU → [pitch, roll]
        self.imu_pub = self.create_publisher(
            Float32MultiArray, "/hexapod/imu", 10
        )

        # ★ NOUVEAU : topic état stabilisation (texte lisible pour debug/Flutter)
        self.imu_status_pub = self.create_publisher(
            String, "/hexapod/imu_status", 10
        )

        if self.ser:
            threading.Thread(
                target=self.read_serial_loop, daemon=True
            ).start()

        self.get_logger().info("Serial Bridge prêt !")

    # ── Envoi commandes vers Arduino ──────────────────────────────────────────
    def cmd_callback(self, msg: String):
        raw = msg.data.strip()
        serial_cmd = raw.split(":", 1)[1] if ":" in raw else raw

        if not self.ser or not self.ser.is_open:
            self.get_logger().error("Port série non disponible !")
            return

        now = time.time()
        if serial_cmd == self._last_cmd and (now - self._last_sent_time) < MIN_INTERVAL:
            return

        self.ser.reset_output_buffer()
        self.ser.write((serial_cmd + "\n").encode())
        self._last_sent_time = now
        self._last_cmd = serial_cmd
        self.get_logger().info(f"→ Arduino: {serial_cmd}")

    # ── Lecture série Arduino — parse IMU ─────────────────────────────────────
    def read_serial_loop(self):
        while rclpy.ok():
            try:
                if self.ser.in_waiting:
                    line = self.ser.readline().decode(errors="ignore").strip()
                    if not line:
                        continue

                    # ★ Parse IMU_DATA
                    if line.startswith("IMU_DATA "):
                        self._handle_imu_line(line)
                    else:
                        # Autres messages Arduino → log normal
                        self.get_logger().info(f"← Arduino: {line}")

            except Exception as e:
                self.get_logger().error(f"Erreur lecture série: {e}")
                break

    def _handle_imu_line(self, line: str):
        """Parse 'IMU_DATA pitch roll' et publie sur /hexapod/imu"""
        try:
            parts = line.split()          # ["IMU_DATA", "2.34", "-1.12"]
            pitch = float(parts[1])
            roll  = float(parts[2])

            # ── Float32MultiArray : [pitch, roll] ──────────────────────────
            imu_msg = Float32MultiArray()
            imu_msg.data = [pitch, roll]
            self.imu_pub.publish(imu_msg)

            # ── Status texte (utile pour Flutter / debug) ──────────────────
            if abs(pitch) < 2.5 and abs(roll) < 2.5:
                status = "STABLE"
            else:
                parts_status = []
                if pitch >  2.5: parts_status.append("AVANT")
                if pitch < -2.5: parts_status.append("ARRIERE")
                if roll  >  2.5: parts_status.append("DROITE")
                if roll  < -2.5: parts_status.append("GAUCHE")
                status = "+".join(parts_status)

            status_msg = String()
            status_msg.data = f"P:{pitch:.1f} R:{roll:.1f} [{status}]"
            self.imu_status_pub.publish(status_msg)

        except (IndexError, ValueError) as e:
            self.get_logger().warn(f"Parse IMU échoué: '{line}' → {e}")

    def destroy_node(self):
        if self.ser and self.ser.is_open:
            self.ser.write(b"STOP\n")
            self.ser.close()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = SerialBridge()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == "__main__":
    main()
