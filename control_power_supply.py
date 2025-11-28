from datetime import datetime
import time
import csv
from bk_precision_1687b import connect_power_supply, set_voltage, set_current, get_voltage_and_current, turn_output_on, turn_output_off

# todos:
#   - handle any errors or lack of comms
#   - get command working to read current and voltage from power supply

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#timestamp = time.time()
log_file = 'power_supply_log_' + str(timestamp) +'.csv'

def initialize_csv_log():
   try:
      with open(log_file, mode='a', newline='') as file:
         writer = csv.writer(file)
         # check if file is empty to add headers (voltage, current, timestamp)
         if file.tell() == 0:
            writer.writerow(['Timestamp', 'Voltage (V)', 'Current (A)', 'Display Voltage (V)', 'Display Current (A)'])
   except Exception as e:
      print(f"error initizing csv log: {e}")

def log_data(voltage, current, display_voltage, display_current):
   try:
      with open(log_file, mode='a', newline='') as file:
         writer = csv.writer(file)
         timestamp = time.strftime('%Y-%m-%d_%H:%M:%S', time.localtime())
         writer.writerow([timestamp, voltage, current, display_voltage, display_current])
   except Exception as e:
      print(f"error logging data to csv: {e}")

def handle_bounds(power_supply, voltage, orig_display_voltage, lower_bound, upper_bound):
      max_retries = 5
      retries = 0

      #retry setting the voltage if not within 0.05V of commanded voltage
      print(f"power supply voltage not reading programmed voltage, retrying")
      while retries < max_retries:
         set_voltage(power_supply, voltage)
         time.sleep(1)
         display_voltage, display_current = get_voltage_and_current(power_supply)
         if (lower_bound <= display_voltage <= upper_bound):
            return display_voltage, display_current
         else:
            retries += 1
            time.sleep(1)
      if retries == max_retries:
         print(f"failed to set power supply to commanded voltage, continuing test")
         return None,None

def step_voltage(power_supply, start_voltage, end_voltage, step_size, wait_time, current):
   voltage = start_voltage
   while voltage <= end_voltage:
      turn_output_off(power_supply)
      time.sleep(3)

      set_voltage(power_supply, voltage)
      set_current(power_supply, current)
      print(f"voltage set to: {voltage}V, current set to: {current}A")

      turn_output_on(power_supply)
      time.sleep(3)

      display_voltage, display_current = get_voltage_and_current(power_supply)
      time.sleep(1)
      print(f"power supply voltage: {display_voltage}V, current: {display_current}A")

      #setting retry bounds to +/- 0.05V
      lower_bound = voltage - 0.05
      upper_bound = voltage + 0.05

      if not (lower_bound <= display_voltage <= upper_bound):
         display_voltage, display_current = handle_bounds(power_supply, voltage, display_voltage, lower_bound, upper_bound)

      time.sleep(wait_time)

      log_data(voltage, current, display_voltage, display_current)

      #time.sleep(wait_time) # wait before stepping again

      voltage += step_size # step the voltage by step size
      voltage = round(voltage, 2)

def main():
   power_supply = connect_power_supply()
   
   if power_supply:
      initialize_csv_log()

      # set default voltage and currents
      # todo: make these passable

      start_voltage = 14 #4.5
      end_voltage = 17
      step_size = 0.1
      wait_time = 5
      current = 0.9

      turn_output_on(power_supply)
      #time.sleep(1)
      step_voltage(power_supply, start_voltage, end_voltage, step_size, wait_time, current)
      #time.sleep(1)
      #turn_output_off(power_supply)

if __name__ == "__main__":
   main()
