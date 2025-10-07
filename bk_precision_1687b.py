# serial remote control program for the BK Precision 1687B power supply
# connection is 9600 8N1 BAUD

# todos
# log control and outputs to a file
# strengthen looping logic for automation testing
# read voltage and current from power supply

import serial
import time

serial_port = '/dev/ttyUSB0'  # specify serial connection to power supply

# open the serial connection
def connect_power_supply():
    try:
        # set up the serial connection
        power_supply = serial.Serial(serial_port, baudrate=9600, timeout=1)
        print(f"Successfully connected to power supply on {serial_port}.")
        return power_supply
    except Exception as e:
        print(f"Error connecting to the power supply: {e}")
        return None

def send_command(power_supply, command):
    """ Send a command to the power supply and wait for a response """
    try:
        power_supply.write(f'{command}\r\n'.encode())
        time.sleep(0.1)  # wait for the command to be processed
        response = power_supply.readline().decode().strip()  # read the response
        return response
    except Exception as e:
        print(f"Error sending command: {e}")
        return None

def query_device_id(power_supply):
    response = send_command(power_supply, '*IDN?')
    if response:
        print(f"Device Response: {response}")

def format_number(num):
    # this function can take in either 8 or 8.0 or 8.5 and return 008 or 008 or 085
    # convert to integer if it's a whole number (either int or float)
    if num == int(num):  # this checks if the number is a whole number
        num = int(num)
    return f"{int(round(num*10)):03d}"  # zero pad to 3 digits

def set_voltage(power_supply, voltage):
    # send the command to set the voltage
    formatted_voltage = format_number(voltage)
    command = f"VOLT{formatted_voltage}"
    response = send_command(power_supply, command)
    if response:
        print(f"Voltage set to: {voltage} V")

def set_current(power_supply, current):
    # send the command to set the current
    formatted_current = format_number(current)
    command = f"CURR{formatted_current}"
    response = send_command(power_supply, command)
    if response:
        print(f"Current set to: {current} A")

def turn_output_on(power_supply):
    # turn on the output, 0 is on
    command = f"SOUT0"
    response = send_command(power_supply, command)
    print("Output turned ON.", response)

def turn_output_off(power_supply):
    # turn off the output, 1 is off
    command = f"SOUT1"
    response = send_command(power_supply, command)
    print("Output turned OFF.", response)

def main():
    # connect to the power supply
    power_supply = connect_power_supply()

    if power_supply:
        # set voltage to 5V
        set_voltage(power_supply, 5)

        # set current to 2.5A
        set_current(power_supply, 2.5)

        # turn the output ON
        turn_output_on(power_supply)

        # turn the output OFF
        turn_output_off(power_supply)

main()
