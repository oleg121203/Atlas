import asyncio
import time
import threading
import json

from real_time_collaboration import RealTimeCollaboration

if __name__ == "__main__":
    # Give a moment before starting clients
    time.sleep(1)

    # Create multiple collaboration clients to simulate different users
    client1 = RealTimeCollaboration()
    client2 = RealTimeCollaboration()

    print("Starting collaboration clients...")
    client1.start()
    client2.start()

    # Give clients time to connect
    time.sleep(2)

    print("Sending test updates from clients...")
    # Simulate workflow updates from different users
    asyncio.run_coroutine_threadsafe(
        client1.send_update('workflow_update', {
            'user': 'User1',
            'workflow_id': 'WF001',
            'change': 'Updated step 1'
        }),
        client1.loop
    )

    asyncio.run_coroutine_threadsafe(
        client2.send_update('workflow_update', {
            'user': 'User2',
            'workflow_id': 'WF001',
            'change': 'Updated step 2'
        }),
        client2.loop
    )

    # Simulate presence updates
    asyncio.run_coroutine_threadsafe(
        client1.send_update('presence_update', {
            'user': 'User1',
            'status': 'editing WF001'
        }),
        client1.loop
    )

    # Keep the demo running to observe real-time updates
    try:
        print("Demo running. Press Ctrl+C to exit.")
        time.sleep(20)  # Run for 20 seconds to observe interactions
    except KeyboardInterrupt:
        print("Demo terminated by user.")
    finally:
        print("Shutting down clients...")
        client1.stop()
        client2.stop()
        print("Demo completed.")
