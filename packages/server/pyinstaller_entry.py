#!/usr/bin/env python3
"""PyInstaller entry point for TestCode server."""
import sys
import os

os.chdir(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.getcwd())

from testcode_server.app import main
main()
