import subprocess
import re

def get_i2c_scan(bus=7):
    # Executes 'i2cdetect -y 7' and captures the output
    result = subprocess.run(['i2cdetect', '-y', '-r', str(bus)], capture_output=True, text=True)
    return result.stdout


def parse_i2c_addresses(output):
    # Regex breakdown:
    # [0-9a-f]{2}  -> matches exactly two hex characters
    # (?=\s|$)     -> "lookahead" to ensure it's followed by a space or end of line
    # (?!:)        -> "negative lookahead" to ignore labels ending in colons (like 10:)
    
    # We find all matches, then filter out the "--" placeholders
    matches = re.findall(r'(?<![:\w])[0-9a-f]{2}(?=\s|$)', output)
    
    # Prepend '0x' to make them standard hex strings
    return [f"0x{addr}" for addr in matches]


def get_i2c_address(bus=7):
    raw_data = get_i2c_scan(7)
    found_addresses = parse_i2c_addresses(raw_data)

    # Convert strings to actual integers
    hex_numbers = [int(addr, 16) for addr in found_addresses]

    return hex_numbers
