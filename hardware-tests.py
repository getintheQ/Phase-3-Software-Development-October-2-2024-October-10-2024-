import RPi.GPIO as GPIO
import spidev
import time
import sys
from datetime import datetime

class HardwareTest:
    def __init__(self):
        # Initialize GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        # Pin Definitions
        self.PINS = {
            'PUMP_PWM': 18,
            'PUMP_DIR1': 23,
            'PUMP_DIR2': 24,
            'POWDER_PWM': 19,
            'POWDER_DIR1': 25,
            'POWDER_DIR2': 26,
            'HEATER': 12,
            'WATER_TRIGGER': 16,
            'WATER_ECHO': 17,
            'VALVE': 22
        }
        
        # Setup GPIO pins
        for pin in self.PINS.values():
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)
        GPIO.setup(self.PINS['WATER_ECHO'], GPIO.IN)
        
        # Initialize SPI for temperature sensors
        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)  # SPI0
        self.spi.max_speed_hz = 5000000
        self.spi.mode = 0

    def test_temperature_sensors(self):
        """Test both temperature sensors"""
        print("\n=== Testing Temperature Sensors ===")
        
        try:
            # Test Sensor 1
            print("Testing Temperature Sensor 1 (Inlet)...")
            self.spi.chip_select = 0
            raw = self.spi.readbytes(4)
            temp1 = ((raw[0] << 8) | raw[1]) >> 2
            temp1 = temp1 * 0.25
            print(f"Sensor 1 Reading: {temp1:.1f}°C")
            
            # Test Sensor 2
            print("Testing Temperature Sensor 2 (Outlet)...")
            self.spi.chip_select = 1
            raw = self.spi.readbytes(4)
            temp2 = ((raw[0] << 8) | raw[1]) >> 2
            temp2 = temp2 * 0.25
            print(f"Sensor 2 Reading: {temp2:.1f}°C")
            
            if -10 < temp1 < 100 and -10 < temp2 < 100:
                print("✓ Temperature sensors working")
                return True
            else:
                print("✗ Temperature readings out of range")
                return False
                
        except Exception as e:
            print(f"✗ Temperature sensor error: {str(e)}")
            return False

    def test_pump_motor(self):
        """Test pump motor control"""
        print("\n=== Testing Pump Motor ===")
        
        try:
            # Setup PWM
            pump_pwm = GPIO.PWM(self.PINS['PUMP_PWM'], 1000)
            pump_pwm.start(0)
            
            # Test forward direction
            print("Testing forward direction...")
            GPIO.output(self.PINS['PUMP_DIR1'], GPIO.HIGH)
            GPIO.output(self.PINS['PUMP_DIR2'], GPIO.LOW)
            
            # Gradually increase speed
            for duty in range(0, 101, 20):
                pump_pwm.ChangeDutyCycle(duty)
                print(f"Speed: {duty}%")
                time.sleep(1)
            
            # Stop
            pump_pwm.ChangeDutyCycle(0)
            time.sleep(1)
            
            # Test reverse direction
            print("\nTesting reverse direction...")
            GPIO.output(self.PINS['PUMP_DIR1'], GPIO.LOW)
            GPIO.output(self.PINS['PUMP_DIR2'], GPIO.HIGH)
            
            # Gradually increase speed
            for duty in range(0, 101, 20):
                pump_pwm.ChangeDutyCycle(duty)
                print(f"Speed: {duty}%")
                time.sleep(1)
            
            # Stop
            pump_pwm.ChangeDutyCycle(0)
            pump_pwm.stop()
            
            print("✓ Pump motor test complete")
            return True
            
        except Exception as e:
            print(f"✗ Pump motor error: {str(e)}")
            return False

    def test_powder_motor(self):
        """Test powder dispensing motor"""
        print("\n=== Testing Powder Motor ===")
        
        try:
            # Setup PWM
            powder_pwm = GPIO.PWM(self.PINS['POWDER_PWM'], 1000)
            powder_pwm.start(0)
            
            # Test operation
            print("Testing powder dispenser...")
            GPIO.output(self.PINS['POWDER_DIR1'], GPIO.HIGH)
            GPIO.output(self.PINS['POWDER_DIR2'], GPIO.LOW)
            
            # Run at different speeds
            speeds = [20, 50, 80]
            for speed in speeds:
                print(f"Running at {speed}% speed")
                powder_pwm.ChangeDutyCycle(speed)
                time.sleep(2)
            
            # Stop
            powder_pwm.ChangeDutyCycle(0)
            powder_pwm.stop()
            
            print("✓ Powder motor test complete")
            return True
            
        except Exception as e:
            print(f"✗ Powder motor error: {str(e)}")
            return False

    def test_heater_control(self):
        """Test heater SSR control"""
        print("\n=== Testing Heater Control ===")
        
        try:
            # Setup PWM for heater
            heater_pwm = GPIO.PWM(self.PINS['HEATER'], 1)
            heater_pwm.start(0)
            
            print("Testing heater power levels...")
            powers = [0, 25, 50, 75, 100]
            
            for power in powers:
                print(f"Setting heater to {power}%")
                heater_pwm.ChangeDutyCycle(power)
                time.sleep(3)
                
                # Read temperature to verify heating
                self.spi.chip_select = 1  # Outlet temperature sensor
                raw = self.spi.readbytes(4)
                temp = ((raw[0] << 8) | raw[1]) >> 2
                temp = temp * 0.25
                print(f"Current temperature: {temp:.1f}°C")
            
            # Turn off heater
            heater_pwm.ChangeDutyCycle(0)
            heater_pwm.stop()
            
            print("✓ Heater control test complete")
            return True
            
        except Exception as e:
            print(f"✗ Heater control error: {str(e)}")
            return False

    def test_water_level_sensor(self):
        """Test water level sensor"""
        print("\n=== Testing Water Level Sensor ===")
        
        try:
            print("Measuring water level...")
            
            # Take multiple readings
            readings = []
            for _ in range(5):
                GPIO.output(self.PINS['WATER_TRIGGER'], GPIO.HIGH)
                time.sleep(0.00001)
                GPIO.output(self.PINS['WATER_TRIGGER'], GPIO.LOW)
                
                while GPIO.input(self.PINS['WATER_ECHO']) == 0:
                    pulse_start = time.time()
                
                while GPIO.input(self.PINS['WATER_ECHO']) == 1:
                    pulse_end = time.time()
                
                pulse_duration = pulse_end - pulse_start
                distance = pulse_duration * 17150  # Speed of sound = 34300 cm/s
                readings.append(distance)
                time.sleep(0.1)
            
            # Calculate average
            avg_distance = sum(readings) / len(readings)
            print(f"Average distance to water surface: {avg_distance:.1f} cm")
            
            if 0 < avg_distance < 100:  # Reasonable range for tank
                print("✓ Water level sensor working")
                return True
            else:
                print("✗ Water level reading out of range")
                return False
                
        except Exception as e:
            print(f"✗ Water level sensor error: {str(e)}")
            return False

    def test_circulation_valve(self):
        """Test circulation valve operation"""
        print("\n=== Testing Circulation Valve ===")
        
        try:
            print("Testing valve operation...")
            
            # Open valve
            print("Opening valve...")
            GPIO.output(self.PINS['VALVE'], GPIO.HIGH)
            time.sleep(2)
            
            # Close valve
            print("Closing valve...")
            GPIO.output(self.PINS['VALVE'], GPIO.LOW)
            time.sleep(2)
            
            print("✓ Valve operation test complete")
            return True
            
        except Exception as e:
            print(f"✗ Valve operation error: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all hardware tests"""
        print("Starting Hardware Tests...")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 50)
        
        results = {
            "Temperature Sensors": self.test_temperature_sensors(),
            "Pump Motor": self.test_pump_motor(),
            "Powder Motor": self.test_powder_motor(),
            "Heater Control": self.test_heater_control(),
            "Water Level Sensor": self.test_water_level_sensor(),
            "Circulation Valve": self.test_circulation_valve()
        }
        
        print("\n=== Test Results Summary ===")
        for test, passed in results.items():
            status = "✓ PASS" if passed else "✗ FAIL"
            print(f"{test}: {status}")
        
        # Overall result
        if all(results.values()):
            print("\nAll tests passed successfully!")
        else:
            print("\nSome tests failed. Please check the results above.")
        
        # Cleanup
        GPIO.cleanup()

if __name__ == "__main__":
    try:
        tester = HardwareTest()
        tester.run_all_tests()
    except KeyboardInterrupt:
        print("\nTests interrupted by user")
        GPIO.cleanup()
    except Exception as e:
        print(f"\nTest suite error: {str(e)}")
        GPIO.cleanup()
