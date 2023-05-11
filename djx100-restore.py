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
import binascii

HEADER_MAGIC_NUMBER = b'X100'
HEADER_DATA_SIZE = 128000
HEADER_LENGTH = 256

def transmit_command(ser, cmd):
    try:
        ser.write((cmd + '\r').encode())
    except serial.SerialTimeoutException:
        print("Error: Write operation timed out. Please check the connection and try again.")
        exit(-1)
    ser.readline()
    response = ser.readline().strip().decode()
    return response

def main():
    parser = argparse.ArgumentParser(description='Alinco DJ-X100 memory restore script', allow_abbrev=False)
    parser.add_argument('-i', '--input', type=str, required=True, help='Input file name (required)')
    parser.add_argument('-p', '--port', type=str, required=True, help='Serial port name (required)')
    parser.add_argument('-b', '--baudrate', type=int, default=115200, help='Baud rate (default: 115200)')
    parser.add_argument('--skip-crc-check', action='store_true', help='Skip CRC integrity check for the input file')
    parser.add_argument('--skip-version-check', action='store_true', help='Skip device firmware version check')
    args = parser.parse_args()

    start_addr = 0x20000
    end_addr = 0x3f3ff

    if not os.path.exists(args.input):
        print(f"Error: The file '{args.input}' does not exist. Please check the file name and try again.")
        exit(0)

    try:
        with open(args.input, 'rb') as f:
            magic_number = f.read(4)
            version = int.from_bytes(f.read(1), byteorder='little')
            data_size = int.from_bytes(f.read(4), byteorder='little')
            
            if magic_number != HEADER_MAGIC_NUMBER:
                print("Error: Invalid magic number. Please check the input file.")
                exit(-1)
            if not version in (1, 2):
                print("Error: Unsupported file version. Please check the input file.")
                exit(-1)
            if version == 1:
                print(f"Notice: Data version of {args.input} is 1, which does not contain a CRC in the header. Skipping CRC check.")
            if version >= 2 and not args.skip_crc_check:
                f.seek(0xFC)
                header_crc = int.from_bytes(f.read(4), byteorder='little')
                crc = binascii.crc32(f.read())
                if header_crc != crc:
                    print("Error: CRC mismatch. Please check the integrity of the input file.")
                    print("If you want to skip the CRC check, you can specify the --skip-crc-check option on the command line.")
                    exit(-1)

            f.seek(0, os.SEEK_END)
            actual_data_size = f.tell() - HEADER_LENGTH
            if data_size != actual_data_size:
                print("Error: Invalid data size. Please check the input file.")
                exit(-1)

            f.seek(HEADER_LENGTH, os.SEEK_SET)
            data = f.read(data_size)
    except PermissionError as e:
        print(f"Error: {e}. Could not open the file '{args.input}' for reading. Please check the file permissions.")
        exit(-1)

    if start_addr < 0x20000:
        print('警告: 重要なデータを含むメモリを上書きしようとしているためデバイスが壊れる可能性があります。この操作は元に戻せません。本当に続行しますか？')
        confirm = input('Warning: You are about to overwrite memory that contains important data, which may potentially brick the device. This operation is irreversible. Are you sure you want to proceed? (y/N):')
        if confirm.lower() != 'y':
            print("Aborted.")
            exit(0)

    try:
        ser = serial.Serial(args.port, args.baudrate, timeout=5, write_timeout=5)
    except serial.serialutil.SerialException as e:
        print(f"Error: {e}. Could not open port '{args.port}'. Please check the port name and try again.")
        exit(-1)

    if not args.skip_version_check:
        response = transmit_command(ser, 'AL~VER')
        if response != 'ver 1.00-003':
            print("Error: Device returned an unexpected firmware version number. Please check the device and try again.")
            print("If you want to skip the firmware version check, add --skip-version-check to the command line options.")
            exit(-1)

    response = transmit_command(ser, 'AL~DJ-X100')
    if response != 'OK':
        print("Error: No response from the device or timed out. Please check the connection and try again.")
        exit(-1)

    page_total = int((end_addr - start_addr) / 0x100) + 1
    current_page = 0

    for addr in range(start_addr, end_addr + 1, 0x100):
        current_page += 1
        offset = addr - start_addr

        # Read current data from the device
        response = transmit_command(ser, f'AL~F{addr:05X}M')
        current_data = bytes.fromhex(response)

        # Compare and write new data if it's different
        for i in range(0, 256, 128):
            new_data = data[offset + i:offset + i + 128]
            if new_data != current_data[i:i + 128]:
                response = transmit_command(ser, f'AL~F{addr + i:05X}W{new_data.hex().upper()}')
                if response != 'OK':
                    print(f"Error: Failed to write data at address {addr + i:05X}. Please check the connection and try again.")
                    exit(-1)

        print(f"Restoring memory: {current_page}/{page_total}", end='\r')

    # Restart the device
    transmit_command(ser, 'AL~RESTART')
    print("\nMemory restore complete. Device has been restarted.")

    ser.close()

if __name__ == '__main__':
    main()
