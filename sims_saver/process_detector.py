"""
Process detection for The Sims 4 with fuzzy matching.
Uses rapidfuzz for intelligent process name matching.
"""

import platform
from typing import Optional

import psutil
from rapidfuzz import fuzz


class ProcessDetector:
    """Detects if The Sims 4 is running using fuzzy process name matching."""

    # Known Sims 4 process names across platforms
    KNOWN_SIMS4_PROCESSES = [
        # Windows
        "ts4.exe",
        "ts4_x64.exe",
        "TS4_x64_fpb",
        "TS4_x64_fpb.exe",
        "the sims 4.exe",
        "sims4.exe",
        # macOS
        "the sims 4",
        "ts4",
        "ts4_x64",
        "sims 4",
        # With various capitalizations
        "TS4.exe",
        "TS4_x64.exe",
        "The Sims 4.exe",
        "The Sims 4",
        "TS4",
        "TS4_x64",
    ]

    # Minimum similarity threshold for fuzzy matching (0-100)
    SIMILARITY_THRESHOLD = 90
    
    # Process name must contain one of these substrings to be considered for fuzzy matching
    REQUIRED_SUBSTRINGS = ["sims", "ts4"]

    def __init__(self):
        self._cached_process_name: Optional[str] = None

    def is_sims4_running(self) -> bool:
        """
        Check if The Sims 4 is currently running.
        
        Returns:
            True if Sims 4 is detected, False otherwise.
        """
        detected_process = self._find_sims4_process()
        return detected_process is not None

    def is_process_running(self, process_name: str) -> bool:
        """
        Check if a specific process is running.
        
        Args:
            process_name: Name of the process to check for.
            
        Returns:
            True if the process is running, False otherwise.
        """
        try:
            process_name_lower = process_name.lower()
            for proc in psutil.process_iter(["name"]):
                try:
                    name = proc.info.get("name")
                    if name and name.lower() == process_name_lower:
                        return True
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
        except Exception as e:
            print(f"Error checking process: {e}")
        return False

    def _find_sims4_process(self) -> Optional[str]:
        """
        Find The Sims 4 process using fuzzy matching.
        
        Returns:
            The name of the detected process, or None if not found.
        """
        try:
            for proc in psutil.process_iter(["pid", "name"]):
                try:
                    process_name = proc.info.get("name")
                    if not process_name:
                        continue

                    # First, try exact match (case-insensitive)
                    process_name_lower = process_name.lower()
                    for known_name in self.KNOWN_SIMS4_PROCESSES:
                        if process_name_lower == known_name.lower():
                            self._cached_process_name = process_name
                            return process_name

                    # Only attempt fuzzy matching if process name contains a required substring
                    # This prevents false positives like "smss.exe" matching "sims"
                    has_required_substring = any(
                        substr in process_name_lower 
                        for substr in self.REQUIRED_SUBSTRINGS
                    )
                    
                    if has_required_substring:
                        best_score = 0
                        for known_name in self.KNOWN_SIMS4_PROCESSES:
                            # Use ratio for stricter matching (no tokenization)
                            score = fuzz.ratio(
                                process_name_lower, known_name.lower()
                            )
                            best_score = max(best_score, score)

                        if best_score >= self.SIMILARITY_THRESHOLD:
                            self._cached_process_name = process_name
                            return process_name

                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue

        except Exception as e:
            print(f"Error scanning processes: {e}")

        return None

    def get_detected_process_name(self) -> Optional[str]:
        """
        Get the name of the last detected Sims 4 process.
        
        Returns:
            The process name if detected, None otherwise.
        """
        return self._cached_process_name

    @staticmethod
    def get_all_running_processes() -> list[str]:
        """
        Get a list of all currently running process names.
        Useful for debugging or custom process selection.
        
        Returns:
            List of unique process names.
        """
        processes = set()
        try:
            for proc in psutil.process_iter(["name"]):
                try:
                    name = proc.info.get("name")
                    if name:
                        processes.add(name)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
        except Exception as e:
            print(f"Error getting process list: {e}")

        return sorted(processes)

    @staticmethod
    def calculate_similarity(name1: str, name2: str) -> int:
        """
        Calculate similarity score between two process names.
        
        Args:
            name1: First process name
            name2: Second process name
            
        Returns:
            Similarity score from 0-100
        """
        return fuzz.ratio(name1.lower(), name2.lower())
