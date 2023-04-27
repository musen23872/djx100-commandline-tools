# MIT License
#
# Copyright (c) 2023 musen23872
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import serial
import argparse
import os

def main():
    parser = argparse.ArgumentParser(description='Alinco DJ-X100 **Unofficial** Memory Backup Script')
    parser.add_argument('-o', '--output', type=str, required=True, help='Output file name (required)')
    parser.add_argument('-p', '--port', type=str, required=True, help='Serial port name (required)')
    parser.add_argument('-f', '--force', action='store_true', help='Overwrite output file without confirmation')
    parser.add_argument('-b', '--baudrate', type=int, default=115200, help='Baud rate (default: 115200)')
    args = parser.parse_args()

    header_magic_number = 'X100'
    header_version = 1
    header_data_size = 128000
    header_comment = 'Alinco DJ-X100 **Unofficial** Memory Backup Data'

    start_addr = 0x20000
    end_addr = 0x3f3ff

    try:
        ser = serial.Serial(args.port, args.baudrate, timeout=5, write_timeout=5)
    except serial.serialutil.SerialException as e:
        print(f"Error: {e}. Could not open port '{args.port}'. Please check the port name and try again.")
        exit(-1)

    cmd = 'AL~DJ-X100\r'
    try:
        ser.write(cmd.encode())
    except serial.SerialTimeoutException:
        print("Error: Write operation timed out. Please check the connection and try again.")
        exit(-1)

    ser.readline()
    response = ser.readline().strip().decode()
    if response != 'OK':
        print("Error: No response from the device or timed out. Please check the connection and try again.")
        exit(-1)

    page_total = int((end_addr - start_addr) / 0x100) + 1

    if not args.force and os.path.exists(args.output):
        confirm = input(f"The file '{args.output}' already exists. Do you want to overwrite it? (y/N): ")
        if confirm.lower() != 'y':
            print("Aborted.")
            exit(0)

    try:
        with open(args.output, 'wb') as f:
            header = \
                (header_magic_number + '\0' * 4)[:4].encode() + \
                header_version.to_bytes(1, 'little') + \
                header_data_size.to_bytes(4, 'little') + \
                (header_comment + '\0' * 64)[:64].encode()
            header += ('\0' * 256).encode()
            f.write(header[:256])

            for current_page, addr in enumerate(range(start_addr, end_addr, 0x100), start=1):
                cmd = f'AL~F{addr:05X}M\r'
                print(f'\rReading memory page {current_page} of {page_total}', end='', flush=True)
                try:
                    ser.write(cmd.encode())
                except serial.SerialTimeoutException:
                    print("\nError: Write operation timed out. Please check the connection and try again.")
                    exit(-1)

                ser.readline()
                response = ser.readline().strip().decode()
                if not response:
                    print("\nError: No response from the device or timed out. Please check the connection and try again.")
                    exit(-1)
                binary_data = bytes.fromhex(response)
                f.write(binary_data)

            print("\nMemory backup completed successfully. Saved to:", args.output)
    except PermissionError as e:
        print(f"Error: {e}. Could not open the file '{args.output}' for writing. Please check the file permissions.")

if __name__ == '__main__':
    main()

