"""
Spotify Control Plugin for Atlas.

This plugin provides Spotify integration including:
- Playback control (play, pause, skip, previous)
- Volume control
- Current track information
- Playlist management
- Search functionality
"""

import asyncio
import json
import logging
import subprocess
from typing import Any, Dict, List, Optional

from core.plugin_system import PluginBase

logger = logging.getLogger(__name__)


class SpotifyControlPlugin(PluginBase):
    """
    Spotify control plugin for Atlas.

    Provides comprehensive Spotify integration using AppleScript on macOS
    and future support for Spotify Web API.
    """

    def __init__(self, name: str = "spotify_control", version: str = "1.0.0"):
        """Initialize the Spotify control plugin."""
        super().__init__(name, version)
        self._spotify_available = self._check_spotify_availability()
        self._applescript_available = self._check_applescript_availability()

    def _check_spotify_availability(self) -> bool:
        """Check if Spotify is installed and available."""
        try:
            # On macOS, check if Spotify.app exists
            result = subprocess.run(
                [
                    "osascript",
                    "-e",
                    'tell application "System Events" to exists application process "Spotify"',
                ],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return "true" in result.stdout.lower()
        except (subprocess.TimeoutExpired, FileNotFoundError):
            logger.debug("Could not detect Spotify installation")
            return False

    def _check_applescript_availability(self) -> bool:
        """Check if AppleScript (osascript) is available."""
        try:
            result = subprocess.run(
                ["osascript", "-e", "return 1"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            logger.warning("AppleScript not available")
            return False

    async def _run_applescript(self, script: str, timeout: int = 10) -> Dict[str, Any]:
        """
        Run an AppleScript command asynchronously.

        Args:
            script: AppleScript code to execute
            timeout: Command timeout in seconds

        Returns:
            Dict containing command result and output
        """
        if not self._applescript_available:
            return {
                "success": False,
                "error": "AppleScript is not available on this system",
                "output": "",
            }

        try:
            process = await asyncio.create_subprocess_exec(
                "osascript",
                "-e",
                script,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await asyncio.wait_for(
                process.communicate(), timeout=timeout
            )

            result = {
                "success": process.returncode == 0,
                "return_code": process.returncode,
                "output": stdout.decode().strip(),
                "stderr": stderr.decode().strip(),
                "script": script,
            }

            if not result["success"]:
                logger.warning(f"AppleScript failed: {result['stderr']}")
            else:
                logger.debug(f"AppleScript successful: {script[:50]}...")

            return result

        except asyncio.TimeoutError:
            logger.error(f"AppleScript timed out: {script[:50]}...")
            return {
                "success": False,
                "error": f"Script timed out after {timeout} seconds",
                "output": "",
                "script": script,
            }
        except Exception as e:
            logger.error(f"Error running AppleScript: {e}")
            return {"success": False, "error": str(e), "output": "", "script": script}

    def initialize(self) -> None:
        """Initialize the plugin."""
        super().initialize()
        logger.info("Initializing Spotify control plugin")

        if not self._spotify_available:
            logger.warning("Spotify not detected - some features may not work")
        if not self._applescript_available:
            logger.warning("AppleScript not available - plugin functionality limited")

    async def play(self) -> Dict[str, Any]:
        """Start or resume playback."""
        script = 'tell application "Spotify" to play'
        result = await self._run_applescript(script)

        if result["success"]:
            result["message"] = "Playback started"

        return result

    async def pause(self) -> Dict[str, Any]:
        """Pause playback."""
        script = 'tell application "Spotify" to pause'
        result = await self._run_applescript(script)

        if result["success"]:
            result["message"] = "Playback paused"

        return result

    async def next_track(self) -> Dict[str, Any]:
        """Skip to next track."""
        script = 'tell application "Spotify" to next track'
        result = await self._run_applescript(script)

        if result["success"]:
            result["message"] = "Skipped to next track"

        return result

    async def previous_track(self) -> Dict[str, Any]:
        """Go to previous track."""
        script = 'tell application "Spotify" to previous track'
        result = await self._run_applescript(script)

        if result["success"]:
            result["message"] = "Went to previous track"

        return result

    async def get_current_track(self) -> Dict[str, Any]:
        """Get information about the currently playing track."""
        script = """
        tell application "Spotify"
            set trackName to name of current track
            set artistName to artist of current track
            set albumName to album of current track
            set trackDuration to duration of current track
            set playerPosition to player position
            set playerState to player state as string
            return trackName & " | " & artistName & " | " & albumName & " | " & trackDuration & " | " & playerPosition & " | " & playerState
        end tell
        """

        result = await self._run_applescript(script)

        if result["success"] and result["output"]:
            try:
                parts = result["output"].split(" | ")
                if len(parts) >= 6:
                    track_info = {
                        "track_name": parts[0],
                        "artist": parts[1],
                        "album": parts[2],
                        "duration": int(parts[3]) if parts[3].isdigit() else 0,
                        "position": int(float(parts[4]))
                        if parts[4].replace(".", "").isdigit()
                        else 0,
                        "state": parts[5],
                    }
                    result["track_info"] = track_info
                    result["message"] = (
                        f"Now playing: {track_info['track_name']} by {track_info['artist']}"
                    )
                else:
                    result["track_info"] = {
                        "error": "Could not parse track information"
                    }
            except Exception as e:
                result["track_info"] = {"error": f"Failed to parse track info: {e}"}

        return result

    async def set_volume(self, volume: int) -> Dict[str, Any]:
        """
        Set playback volume.

        Args:
            volume: Volume level (0-100)

        Returns:
            Volume change result
        """
        if not 0 <= volume <= 100:
            return {"success": False, "error": "Volume must be between 0 and 100"}

        script = f'tell application "Spotify" to set sound volume to {volume}'
        result = await self._run_applescript(script)

        if result["success"]:
            result["message"] = f"Volume set to {volume}%"

        return result

    async def get_volume(self) -> Dict[str, Any]:
        """Get current volume level."""
        script = 'tell application "Spotify" to return sound volume'
        result = await self._run_applescript(script)

        if result["success"] and result["output"].isdigit():
            volume = int(result["output"])
            result["volume"] = volume
            result["message"] = f"Current volume: {volume}%"

        return result

    async def toggle_shuffle(self) -> Dict[str, Any]:
        """Toggle shuffle mode."""
        script = """
        tell application "Spotify"
            set shuffling to not shuffling
            return shuffling as string
        end tell
        """

        result = await self._run_applescript(script)

        if result["success"]:
            shuffle_state = result["output"].lower() == "true"
            result["shuffle_enabled"] = shuffle_state
            result["message"] = f"Shuffle {'enabled' if shuffle_state else 'disabled'}"

        return result

    async def toggle_repeat(self) -> Dict[str, Any]:
        """Toggle repeat mode."""
        script = """
        tell application "Spotify"
            set repeating to not repeating
            return repeating as string
        end tell
        """

        result = await self._run_applescript(script)

        if result["success"]:
            repeat_state = result["output"].lower() == "true"
            result["repeat_enabled"] = repeat_state
            result["message"] = f"Repeat {'enabled' if repeat_state else 'disabled'}"

        return result

    async def get_player_state(self) -> Dict[str, Any]:
        """Get comprehensive player state information."""
        script = """
        tell application "Spotify"
            set trackName to name of current track
            set artistName to artist of current track
            set albumName to album of current track
            set playerState to player state as string
            set currentVolume to sound volume
            set isShuffling to shuffling as string
            set isRepeating to repeating as string
            return trackName & " | " & artistName & " | " & albumName & " | " & playerState & " | " & currentVolume & " | " & isShuffling & " | " & isRepeating
        end tell
        """

        result = await self._run_applescript(script)

        if result["success"] and result["output"]:
            try:
                parts = result["output"].split(" | ")
                if len(parts) >= 7:
                    player_state = {
                        "track_name": parts[0],
                        "artist": parts[1],
                        "album": parts[2],
                        "state": parts[3],
                        "volume": int(parts[4]) if parts[4].isdigit() else 0,
                        "shuffle": parts[5].lower() == "true",
                        "repeat": parts[6].lower() == "true",
                    }
                    result["player_state"] = player_state
                    result["message"] = "Retrieved player state"
                else:
                    result["player_state"] = {"error": "Could not parse player state"}
            except Exception as e:
                result["player_state"] = {"error": f"Failed to parse player state: {e}"}

        return result

    async def search_and_play(self, query: str) -> Dict[str, Any]:
        """
        Search for and play a track/album/playlist.

        Args:
            query: Search query

        Returns:
            Search and play result
        """
        if not query.strip():
            return {"success": False, "error": "Search query cannot be empty"}

        # This is a simplified implementation
        # In a full implementation, you would use the Spotify Web API
        script = f'''
        tell application "Spotify"
            play track "{query}"
        end tell
        '''

        result = await self._run_applescript(script)

        if result["success"]:
            result["message"] = f"Searching and playing: {query}"
        else:
            # Try alternative search method
            script_alt = f'tell application "Spotify" to search "{query}"'
            result = await self._run_applescript(script_alt)
            if result["success"]:
                result["message"] = f"Search completed for: {query}"

        return result

    def get_dependencies(self) -> List[str]:
        """Return plugin dependencies."""
        return ["command:osascript", "app:Spotify"]

    def shutdown(self) -> None:
        """Shutdown the plugin."""
        logger.info("Shutting down Spotify control plugin")
        super().shutdown()

    def get_metadata(self) -> Dict[str, str]:
        """Return plugin metadata."""
        metadata = super().get_metadata()
        metadata.update(
            {
                "description": "Spotify playback control and integration",
                "capabilities": [
                    "playback_control",
                    "volume_control",
                    "track_information",
                    "shuffle_repeat_control",
                    "basic_search",
                ],
                "spotify_available": str(self._spotify_available),
                "applescript_available": str(self._applescript_available),
                "platform": "macOS (AppleScript)",
            }
        )
        return metadata
