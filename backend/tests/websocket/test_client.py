"""
WebSocket Test Client
Interactive client for testing real-time events

Usage:
    python -m tests.websocket.test_client
"""

import asyncio
import json
import sys
from websockets import connect
from websockets.exceptions import ConnectionClosed


async def test_websocket():
    """Test WebSocket connection and event streaming"""
    uri = "ws://localhost:8000/ws/events"

    print("🎭 Meta-Orchestrator Switchboard - WebSocket Test Client")
    print(f"📞 Connecting to {uri}...")

    try:
        async with connect(uri) as websocket:
            # Receive welcome message
            welcome = await websocket.recv()
            welcome_data = json.loads(welcome)
            print(f"\n✅ Connected!")
            print(f"   Client ID: {welcome_data.get('client_id')}")
            print(f"   Message: {welcome_data.get('message')}")

            # Subscribe to all events
            print("\n📡 Subscribing to all events...")
            await websocket.send(
                json.dumps({"action": "subscribe", "event_types": ["*"]})
            )

            # Receive subscription confirmation
            confirmation = await websocket.recv()
            confirmation_data = json.loads(confirmation)
            print(f"✅ {confirmation_data.get('message')}")
            print(
                f"   Active subscriptions: {confirmation_data.get('active_subscriptions')}"
            )

            # Listen for events
            print("\n🎧 Listening for events (press Ctrl+C to stop)...\n")
            print("-" * 70)

            while True:
                try:
                    message = await websocket.recv()
                    event = json.loads(message)

                    event_type = event.get("type")
                    timestamp = event.get("timestamp")

                    # Format event output
                    if event_type == "pong":
                        print(f"💓 Heartbeat: pong at {timestamp}")
                    else:
                        print(f"\n📨 Event Received:")
                        print(f"   Type: {event_type}")
                        print(f"   Time: {timestamp}")

                        if "data" in event:
                            data = event["data"]
                            # Pretty print data (limited to first 500 chars)
                            data_str = json.dumps(data, indent=2)
                            if len(data_str) > 500:
                                data_str = data_str[:500] + "\n   ... (truncated)"
                            print(f"   Data: {data_str}")

                        print("-" * 70)

                except ConnectionClosed:
                    print("\n❌ Connection closed by server")
                    break
                except json.JSONDecodeError as e:
                    print(f"\n⚠️ Invalid JSON received: {e}")
                except Exception as e:
                    print(f"\n⚠️ Error: {e}")

    except ConnectionRefusedError:
        print(
            "\n❌ Connection refused. Is the server running on http://localhost:8000?"
        )
        print("   Start the server with: python backend/app/main.py")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n👋 Disconnecting...")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()


async def test_subscription_patterns():
    """Test different subscription patterns"""
    uri = "ws://localhost:8000/ws/events"

    print("🎭 Testing Subscription Patterns")
    print(f"📞 Connecting to {uri}...\n")

    async with connect(uri) as websocket:
        # Welcome
        await websocket.recv()
        print("✅ Connected\n")

        # Test 1: Subscribe to task events only
        print("Test 1: Subscribe to task.* events")
        await websocket.send(
            json.dumps({"action": "subscribe", "event_types": ["task.*"]})
        )
        response = json.loads(await websocket.recv())
        print(f"   ✅ {response.get('active_subscriptions')}\n")

        # Test 2: Add execution events
        print("Test 2: Add execution.* events")
        await websocket.send(
            json.dumps({"action": "subscribe", "event_types": ["execution.*"]})
        )
        response = json.loads(await websocket.recv())
        print(f"   ✅ {response.get('active_subscriptions')}\n")

        # Test 3: Unsubscribe from task events
        print("Test 3: Unsubscribe from task.* events")
        await websocket.send(
            json.dumps({"action": "unsubscribe", "event_types": ["task.*"]})
        )
        response = json.loads(await websocket.recv())
        print(f"   ✅ {response.get('active_subscriptions')}\n")

        # Test 4: Get current subscriptions
        print("Test 4: Get current subscriptions")
        await websocket.send(json.dumps({"action": "get_subscriptions"}))
        response = json.loads(await websocket.recv())
        print(f"   ✅ {response.get('active_subscriptions')}\n")

        # Test 5: Ping/Pong
        print("Test 5: Ping/Pong heartbeat")
        await websocket.send(json.dumps({"action": "ping"}))
        response = json.loads(await websocket.recv())
        print(f"   ✅ {response.get('type')} at {response.get('timestamp')}\n")

        print("✅ All subscription tests passed!")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test-subscriptions":
        asyncio.run(test_subscription_patterns())
    else:
        asyncio.run(test_websocket())
