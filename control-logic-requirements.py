import RPi.GPIO as GPIO
import spidev
import time
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import json
from datetime import datetime
import logging

class WaterLevelSensor:
    def __init__(self, trigger_pin, echo_pin):
        self.trigger_pin = trigger_pin
        self.echo_pin = echo_pin
        
        GPIO.setup(trigger_pin, GPIO.OUT)
        GPIO.setup(echo_pin, GPIO.IN)
        
        self.tank_height = 30.0  # cm
        self.min_water_level = 10.0  # 10% of tank height
        
    def measure_distance(self):
        """Measure water level using ultrasonic sensor"""
        GPIO.output(self.trigger_pin, GPIO.HIGH)
        time.sleep(0.00001)
        GPIO.output(self.trigger_pin, GPIO.LOW)
        
        start_time = time.time()
        stop_time = time.time()
        
        while GPIO.input(self.echo_pin) == 0:
            start_time = time.time()
            
        while GPIO.input(self.echo_pin) == 1:
            stop_time = time.time()
            
        time_elapsed = stop_time - start_time
        distance = (time_elapsed * 34300) / 2  # Speed of sound = 343 m/s
        
        return distance
    
    def get_water_percentage(self):
        """Get water level as percentage"""
        distance = self.measure_distance()
        water_height = self.tank_height - distance
        percentage = (water_height / self.tank_height) * 100
        return max(0, min(100, percentage))

class PowderLevelSensor:
    def __init__(self, weight_pin):
        self.weight_pin = weight_pin
        GPIO.setup(weight_pin, GPIO.IN)
        self.powder_max = 1000  # grams
        self.min_powder_level = 20.0  # 20% of max
        
    def get_powder_percentage(self):
        """Get powder level as percentage using load cell"""
        # Simulate load cell reading - replace with actual HX711 code
        current_weight = 500  # Example weight in grams
        percentage = (current_weight / self.powder_max) * 100
        return max(0, min(100, percentage))

class CirculationValve:
    def __init__(self, valve_pin):
        self.valve_pin = valve_pin
        GPIO.setup(valve_pin, GPIO.OUT)
        
    def set_circulation(self, circulate):
        """Control circulation valve"""
        GPIO.output(self.valve_pin, GPIO.HIGH if circulate else GPIO.LOW)

class CoffeeMachineController:
    def __init__(self):
        # GPIO Setup
        GPIO.setmode(GPIO.BCM)
        
        # Temperature control parameters
        self.TEMP_MIN = 45.0
        self.TEMP_MAX = 60.0
        self.INITIAL_HEATER_POWER = 70  # Start at 70% power
        self.INITIAL_FLOW_RATE = 50     # Start at 50% flow
        
        # Initialize sensors and actuators
        self.temp_in = TemperatureSensor(0, 0)    # SPI0.0
        self.temp_out = TemperatureSensor(0, 1)   # SPI0.1
        self.water_sensor = WaterLevelSensor(16, 17)  # Trigger, Echo
        self.powder_sensor = PowderLevelSensor(27)    # Weight sensor
        self.circulation_valve = CirculationValve(22)  # Valve control
        
        # Initialize motors
        self.pump_motor = MotorController(18, 23, 24)  # PWM, DIR1, DIR2
        self.powder_motor = MotorController(19, 25, 26)  # PWM, DIR1, DIR2
        
        # Initialize heater
        self.heater = HeaterController(12)
        
        # System state
        self.system_state = {
            'water_level': 100.0,
            'powder_level': 100.0,
            'current_temp': 20.0,
            'is_circulating': False,
            'heater_power': self.INITIAL_HEATER_POWER,
            'flow_rate': self.INITIAL_FLOW_RATE
        }
        
        # Alerts state
        self.alerts = {
            'low_water': False,
            'low_powder': False,
            'temp_out_of_range': False
        }
        
        # Control flags
        self.running = False
        self.emergency_stop = False
        
        # Setup logging
        logging.basicConfig(filename='coffee_machine.log',
                          level=logging.INFO,
                          format='%(asctime)s - %(levelname)s - %(message)s')
        
        # Start control threads
        self.start_control_loops()

    def temperature_control_loop(self):
        """Temperature control with circulation logic"""
        while not self.emergency_stop:
            if self.running:
                try:
                    # Read temperatures
                    temp_out = self.temp_out.read_temp()
                    self.system_state['current_temp'] = temp_out
                    
                    # Temperature control logic
                    if temp_out < self.TEMP_MIN:
                        # Increase heater power
                        new_power = self.system_state['heater_power'] + 5
                        self.heater.set_power(min(new_power, 100))
                        self.system_state['heater_power'] = new_power
                        # Reduce flow rate to allow more heating
                        new_flow = self.system_state['flow_rate'] - 5
                        self.pump_motor.set_speed(max(new_flow, 30))
                        self.system_state['flow_rate'] = new_flow
                        # Activate circulation
                        self.circulation_valve.set_circulation(True)
                        self.system_state['is_circulating'] = True
                        
                    elif temp_out > self.TEMP_MAX:
                        # Decrease heater power
                        new_power = self.system_state['heater_power'] - 5
                        self.heater.set_power(max(new_power, 0))
                        self.system_state['heater_power'] = new_power
                        # Increase flow rate to cool down
                        new_flow = self.system_state['flow_rate'] + 5
                        self.pump_motor.set_speed(min(new_flow, 100))
                        self.system_state['flow_rate'] = new_flow
                        # Activate circulation
                        self.circulation_valve.set_circulation(True)
                        self.system_state['is_circulating'] = True
                        
                    else:
                        # Temperature in range
                        self.circulation_valve.set_circulation(False)
                        self.system_state['is_circulating'] = False
                    
                    # Update temperature alert
                    self.alerts['temp_out_of_range'] = not (self.TEMP_MIN <= temp_out <= self.TEMP_MAX)
                    
                    logging.info(f"Temp: {temp_out:.1f}°C, Power: {self.system_state['heater_power']}%, "
                               f"Flow: {self.system_state['flow_rate']}%, Circulating: {self.system_state['is_circulating']}")
                    
                except Exception as e:
                    logging.error(f"Temperature control error: {str(e)}")
                    self.emergency_stop = True
                    
            time.sleep(1.0)

    def level_monitoring_loop(self):
        """Monitor water and powder levels"""
        while not self.emergency_stop:
            if self.running:
                try:
                    # Check water level
                    water_level = self.water_sensor.get_water_percentage()
                    self.system_state['water_level'] = water_level
                    self.alerts['low_water'] = water_level < 10.0
                    
                    # Check powder level
                    powder_level = self.powder_sensor.get_powder_percentage()
                    self.system_state['powder_level'] = powder_level
                    self.alerts['low_powder'] = powder_level < 20.0
                    
                    # Log levels
                    logging.info(f"Water Level: {water_level:.1f}%, Powder Level: {powder_level:.1f}%")
                    
                    # Stop process if levels are critically low
                    if water_level < 5.0 or powder_level < 10.0:
                        logging.error("Critical resource level - stopping process")
                        self.stop_process()
                        
                except Exception as e:
                    logging.error(f"Level monitoring error: {str(e)}")
                    self.emergency_stop = True
                    
            time.sleep(5.0)

    def start_process(self, recipe):
        """Start processing with given recipe"""
        try:
            # Check initial conditions
            water_level = self.water_sensor.get_water_percentage()
            powder_level = self.powder_sensor.get_powder_percentage()
            
            if water_level < 10.0:
                raise Exception("Water level too low to start")
            if powder_level < 20.0:
                raise Exception("Powder level too low to start")
            
            # Initialize system
            self.heater.set_power(self.INITIAL_HEATER_POWER)
            self.pump_motor.set_speed(self.INITIAL_FLOW_RATE)
            self.circulation_valve.set_circulation(False)
            
            self.running = True
            logging.info(f"Starting process with recipe: {recipe}")
            
        except Exception as e:
            logging.error(f"Error starting process: {str(e)}")
            self.emergency_stop = True
            raise

class GUI(tk.Tk):
    def __init__(self, controller):
        super().__init__()
        
        self.controller = controller
        self.title("Coffee Machine Control")
        
        # Create frames
        self.status_frame = ttk.LabelFrame(self, text="System Status")
        self.status_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        
        self.control_frame = ttk.LabelFrame(self, text="Control")
        self.control_frame.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        
        self.setup_gui()
        self.update_timer = self.after(1000, self.update_status)

    def setup_gui(self):
        # Status indicators
        ttk.Label(self.status_frame, text="Temperature:").grid(row=0, column=0, sticky="w")
        self.temp_label = ttk.Label(self.status_frame, text="--.-°C")
        self.temp_label.grid(row=0, column=1, sticky="w")
        
        ttk.Label(self.status_frame, text="Water Level:").grid(row=1, column=0, sticky="w")
        self.water_label = ttk.Label(self.status_frame, text="--%")
        self.water_label.grid(row=1, column=1, sticky="w")
        
        ttk.Label(self.status_frame, text="Powder Level:").grid(row=2, column=0, sticky="w")
        self.powder_label = ttk.Label(self.status_frame, text="--%")
        self.powder_label.grid(row=2, column=1, sticky="w")
        
        # Control buttons
        ttk.Button(self.control_frame, text="Start", 
                  command=self.start_process).grid(row=0, column=0, padx=5)
        ttk.Button(self.control_frame, text="Stop", 
                  command=self.stop_process).grid(row=0, column=1, padx=5)
        ttk.Button(self.control_frame, text="Emergency Stop", 
                  command=self.emergency_stop).grid(row=0, column=2, padx=5)

    def update_status(self):
        """Update status display"""
        if self.controller.running:
            # Update temperature
            self.temp_label.config(
                text=f"{self.controller.system_state['current_temp']:.1f}°C",
                foreground="red" if self.controller.alerts['temp_out_of_range'] else "black"
            )
            
            # Update water level
            self.water_label.config(
                text=f"{self.controller.system_state['water_level']:.1f}%",
                foreground="red" if self.controller.alerts['low_water'] else "black"
            )
            
            # Update powder level
            self.powder_label.config(
                text=f"{self.controller.system_state['powder_level']:.1f}%",
                foreground="red" if self.controller.alerts['low_powder'] else "black"
            )
            
            # Check for alerts
            alerts = []
            if self.controller.alerts['low_water']:
                alerts.append("Low Water Level!")
            if self.controller.alerts['low_powder']:
                alerts.append("Low Powder Level!")
            if self.controller.alerts['temp_out_of_range']:
                alerts.append("Temperature Out of Range!")
            
            if alerts and not hasattr(self, 'alert_shown'):
                self.alert_shown = True
                messagebox.showwarning("System Alerts", "\n".join(alerts))
        
        self.update_timer = self.after(1000, self.update_status)

    def start_process(self):
        try:
            recipe = {
                'target_temp': 52.5,  # Middle of range 45-60
                'flow_rate': self.controller.INITIAL_FLOW_RATE,
                'powder_rate': 50.0
            }
            self.controller.start_process(recipe)
            self.alert_shown = False
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def stop_process(self):
        self.controller.stop_process()

    def emergency_stop(self):
        self.controller.emergency_stop_process()
        self.quit()

if __name__ == "__main__":
    try:
        controller = CoffeeMachineController()
        gui = GUI(controller)
        gui.mainloop()
    except Exception as e:
        logging.critical(f"System crash: {str(e)}")
        GPIO.cleanup()
