# serial remote control program for the BK Precision 1687B power supply
# connection is 9600 8N1 BAUD

# todos
# strengthen looping logic for automation testing

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

def format_display_values(num):
    # convert to a float then with the desired decimal point
    if len(num) == 4:
        # format voltage
        return float(num[:len(num)-2] + '.' + num[-2:])
    else:
        # format current
        num = str(num).zfill(5) # zero pad to ensure it's 5 digits
        integer_part = num[:1] # first two digits are integer
        fractional_part = num[2:] # last three digits are fractional
        return float(f"{integer_part}.{fractional_part[:3]}")
        #return float(num[:len(num)-3] + '.' + num[-3:])

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

def get_voltage_and_current(power_supply):
    # send the command to get power supply display voltage and current
    command = f"GETD"
    response = send_command(power_supply, command)

    # handle the "OK" sent in response to the command after the values
    lines = response.split('\r') # split based on CR
    if len(lines) > 1:
        # first line is the voltage and current data, second line is OK
        # which we can ignore OK
        response = lines[0]
    # split the returned value into voltage and current
    voltage = response[:4]
    current = response[4:]
    voltage = format_display_values(voltage)
    current = format_display_values(current)
    if response:
        print(f"     Voltage reading is: {voltage} V")
        print(f"     Current reading is: {current} A")

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
