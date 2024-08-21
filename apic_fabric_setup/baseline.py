#! /usr/bin/env python
"""
Python script to configure the DevNet Always On APIC Sandbox
for use in the ACI Learning Labs.

Requirements:
  - ACI Cobra 3.0-1k or higher
"""

from startup_script import configure_apic


def main():
    print("\n\nStarting the APIC setup...")
    configure_apic()
    print("APIC setup complete.\n\n")


if __name__ == "__main__":
    main()
