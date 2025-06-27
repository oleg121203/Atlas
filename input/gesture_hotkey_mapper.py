import platform
from typing import Any, Dict

try:
    import keyboard
except ImportError:
    keyboard = None


class GestureHotkeyMapper:
    """Maps gestures and hotkeys to specific workflow commands"""

    def __init__(self):
        self.hotkeys: Dict[str, Dict[str, Any]] = {}
        self.is_listening = False
        self.listener_thread = None
        self.is_mac = platform.system() == "Darwin"

    def register_hotkey(self, hotkey: str, command: Dict[str, Any]) -> None:
        """Register a hotkey combination to a specific command

        Args:
            hotkey (str): Hotkey combination (e.g., "ctrl+shift+w")
            command (Dict[str, Any]): Command to execute when hotkey is pressed
        """
        # Convert hotkey to lowercase to handle variations
        hotkey = hotkey.lower()
        # On macOS, try to map 'ctrl' to 'command' if applicable
        if self.is_mac and "ctrl" in hotkey:
            mac_hotkey = hotkey.replace("ctrl", "command")
            self.hotkeys[mac_hotkey] = command
            print(
                f"Registered macOS hotkey '{mac_hotkey}' for action: {command.get('action', 'unknown')}"
            )
            if keyboard and self.is_listening:
                try:
                    keyboard.add_hotkey(
                        mac_hotkey, self._handle_hotkey, args=(mac_hotkey,)
                    )
                except (ValueError, OSError) as e:
                    print(f"Failed to register macOS hotkey '{mac_hotkey}': {e}")
                    print(
                        "Hotkey functionality may be limited on this system. On macOS, you may need to run the script with sudo or adjust permissions for keyboard access."
                    )

        self.hotkeys[hotkey] = command
        print(
            f"Registered hotkey '{hotkey}' for action: {command.get('action', 'unknown')}"
        )
        if keyboard and self.is_listening:
            # If already listening, add the hotkey immediately
            try:
                keyboard.add_hotkey(hotkey, self._handle_hotkey, args=(hotkey,))
            except (ValueError, OSError) as e:
                print(f"Failed to register hotkey '{hotkey}': {e}")
                print(
                    "Hotkey functionality may be limited on this system. On macOS, you may need to run the script with sudo or adjust permissions for keyboard access."
                )

    def _handle_hotkey(self, hotkey: str) -> None:
        """Handle hotkey press events

        Args:
            hotkey (str): Hotkey combination that was pressed
        """
        if hotkey in self.hotkeys:
            command = self.hotkeys[hotkey]
            print(f"Hotkey triggered: {hotkey}")
            print(f"Executing command: {command}")
            # Here you would dispatch the command to the appropriate handler
        else:
            print(f"Hotkey {hotkey} not found in mappings")

    def start_listening(self) -> None:
        """Start listening for hotkey events"""
        if not keyboard:
            print("Hotkey listening disabled - keyboard module not available")
            return

        if not self.is_listening:
            self.is_listening = True
            # Register all existing hotkeys
            for hotkey in self.hotkeys:
                try:
                    keyboard.add_hotkey(hotkey, self._handle_hotkey, args=(hotkey,))
                except (ValueError, OSError) as e:
                    print(f"Failed to register hotkey '{hotkey}': {e}")
                    print(
                        "Hotkey functionality may be limited on this system. On macOS, you may need to run the script with sudo or adjust permissions for keyboard access."
                    )
            print("Started listening for hotkeys")
        else:
            print("Already listening for hotkeys")

    def stop_listening(self) -> None:
        """Stop listening for hotkey events"""
        if not keyboard:
            print("Hotkey listening disabled - keyboard module not available")
            return

        if self.is_listening:
            self.is_listening = False
            # Remove all hotkey listeners
            try:
                keyboard.clear_all_hotkeys()
            except (ValueError, OSError) as e:
                print(f"Failed to stop listening for hotkeys: {e}")
            print("Stopped listening for hotkeys")
        else:
            print("Not currently listening for hotkeys")

    def register_gesture(self, gesture_name: str, command: Dict[str, Any]) -> None:
        """Placeholder for gesture registration - not implemented on macOS

        Args:
            gesture_name (str): Name or pattern of the gesture
            command (Dict[str, Any]): Command to execute when gesture is detected
        """
        print(
            f"Gesture support for '{gesture_name}' is not implemented on this platform"
        )
        # On macOS, we skip gesture support due to complexity with trackpad gestures

    def map_workflow_commands(
        self, workflow_id: str, commands: Dict[str, Dict[str, Any]]
    ) -> None:
        """Map a set of workflow-specific commands to hotkeys

        Args:
            workflow_id (str): ID of the workflow these commands belong to
            commands (Dict[str, Dict[str, Any]]): Dictionary of hotkey to command mappings
        """
        for hotkey, command in commands.items():
            # Add workflow ID to command for context
            command["workflow_id"] = workflow_id
            self.register_hotkey(hotkey, command)
