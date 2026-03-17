#!/usr/bin/env python3
"""
Simple state file for bot communication
"""

import os
import json
from pathlib import Path

def get_mode():
    """Get current mode from simple file"""
    try:
        state_file = Path(__file__).parent / "data" / "mode.txt"
        if state_file.exists():
            with open(state_file, 'r') as f:
                mode = f.read().strip()
                print(f"[SIMPLE_STATE] Read mode: {mode}")
                return mode
        else:
            return 'busy'
    except Exception as e:
        print(f"[SIMPLE_STATE] Error reading mode: {e}")
        return 'busy'

def set_mode(mode):
    """Set mode to simple file"""
    try:
        state_file = Path(__file__).parent / "data" / "mode.txt"
        state_file.parent.mkdir(exist_ok=True)
        with open(state_file, 'w') as f:
            f.write(mode)
        print(f"[SIMPLE_STATE] Set mode: {mode}")
    except Exception as e:
        print(f"[SIMPLE_STATE] Error writing mode: {e}")
