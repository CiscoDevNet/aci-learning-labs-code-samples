#! /usr/bin/env python
"""
Python script to configure the DevNet Always On APIC Sandbox
for use in the ACI Learning Labs.

Requirements:
  - ACI Cobra 3.0-1k or higher
"""

# Run startup_script.py
import startup_script

# Run main() from create_snv_apps
import create_snv_apps
create_snv_apps.main()
