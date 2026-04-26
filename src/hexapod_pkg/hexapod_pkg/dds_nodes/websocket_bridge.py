#!/usr/bin/env python3
# websocket_bridge.py — version complète bidirectionnelle

import asyncio
import websockets
import threading
import json
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

WS_PORT = 9090

# Set global des clients Flutter connectés
connected_clients: set = set()

class WebSocketBridge(Node):
    def __init__(self):
        super().__init__("websocket_bridge")

        # ── Existant : commandes Flutter → ROS2 ──────────────────────────
        self.pub = self.create_publisher(String, "/hl_real_cmd", 10)

        # ── Nouveau : stats Jetson → Flutter ─────────────────────────────
        self.create_subscription(
            String,
            "/jetson/system_stats",
            self.on_stats_received,
            10
        )

        self.loop = None  # référence à l'event loop asyncio (définie plus bas)
        self.get_logger().info(f"✅ WebSocket Bridge prêt — port {WS_PORT}")

    def publish_cmd(self, cmd: str):
        """Publie une commande reçue de Flutter vers ROS2."""
        msg = String()
        msg.data = cmd.strip()
        self.pub.publish(msg)
        self.get_logger().info(f"Flutter → ROS2: {cmd}")

    def on_stats_received(self, msg: String):
        """Callback ROS2 : reçoit les stats et les envoie à Flutter."""
        if self.loop is None or not connected_clients:
            return
        # On encapsule dans un objet JSON typé pour que Flutter puisse filtrer
        payload = json.dumps({
            "type": "stats",
            "data": json.loads(msg.data)
        })
        # On planifie le broadcast dans le thread asyncio
        asyncio.run_coroutine_threadsafe(
            broadcast(payload),
            self.loop
        )


async def broadcast(message: str):
    """Envoie un message à tous les clients Flutter connectés."""
    if connected_clients:
        await asyncio.gather(
            *[client.send(message) for client in connected_clients],
            return_exceptions=True  # un client déconnecté ne fait pas crasher
        )


async def handler(websocket, node):
    """Gère un client Flutter : écoute ses commandes + l'ajoute au broadcast."""
    connected_clients.add(websocket)
    node.get_logger().info(
        f"📱 Flutter connecté ({len(connected_clients)} client(s))"
    )
    try:
        async for message in websocket:
            node.publish_cmd(message)
            await websocket.send(f"OK:{message}")
    finally:
        connected_clients.discard(websocket)
        node.get_logger().info("📱 Flutter déconnecté")


async def ws_server(node):
    node.loop = asyncio.get_event_loop()
    async with websockets.serve(
        lambda ws: handler(ws, node),
        "0.0.0.0",
        WS_PORT
    ):
        await asyncio.Future()


def main(args=None):
    rclpy.init(args=args)
    node = WebSocketBridge()
    threading.Thread(target=rclpy.spin, args=(node,), daemon=True).start()
    asyncio.run(ws_server(node))
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()
