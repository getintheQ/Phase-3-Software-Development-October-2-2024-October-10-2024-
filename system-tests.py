import unittest
from unittest.mock import Mock, patch
import time
import logging
from coffee_machine_control import (
    CoffeeMachineController, 
    WaterLevelSensor, 
    PowderLevelSensor, 
    CirculationValve,
    TemperatureSensor,
    MotorController,
    HeaterController
)

class TestCoffeeMachine(unittest.TestCase):
    def setUp(self):
        """Setup test environment with mocked hardware"""
        # Mock GPIO and SPI
        self.gpio_mock = patch('RPi.GPIO').start()
        self.spi_mock = patch('spidev.SpiDev').start()
        
        # Create controller instance
        self.controller = CoffeeMachineController()
        
        # Mock sensor readings
        self.controller.temp_in.read_temp = Mock(return_value=25.0)
        self.controller.temp_out.read_temp = Mock(return_value=25.0)
        self.controller.water_sensor.get_water_percentage = Mock(return_value=100.0)
        self.controller.powder_sensor.get_powder_percentage = Mock(return_value=100.0)

    def tearDown(self):
        """Cleanup after tests"""
        patch.stopall()
        self.controller.stop_process()

    def test_1_initial_conditions(self):
        """Test initial system conditions"""
        print("\nTest 1: Checking initial conditions...")
        
        self.assertEqual(self.controller.TEMP_MIN, 45.0)
        self.assertEqual(self.controller.TEMP_MAX, 60.0)
        self.assertEqual(self.controller.INITIAL_HEATER_POWER, 70)
        self.assertEqual(self.controller.INITIAL_FLOW_RATE, 50)
        self.assertFalse(self.controller.running)
        self.assertFalse(self.controller.emergency_stop)
        
        print("✓ Initial conditions verified")

    def test_2_temperature_control(self):
        """Test temperature control system"""
        print("\nTest 2: Testing temperature control...")
        
        # Test cold temperature response
        print("Testing cold temperature response...")
        self.controller.temp_out.read_temp = Mock(return_value=40.0)  # Below minimum
        self.controller.start_process({'target_temp': 52.5})
        time.sleep(2)  # Allow control loop to respond
        
        self.assertTrue(self.controller.system_state['is_circulating'])
        self.assertTrue(self.controller.system_state['heater_power'] > self.controller.INITIAL_HEATER_POWER)
        print("✓ Cold temperature response correct")
        
        # Test hot temperature response
        print("Testing hot temperature response...")
        self.controller.temp_out.read_temp = Mock(return_value=65.0)  # Above maximum
        time.sleep(2)  # Allow control loop to respond
        
        self.assertTrue(self.controller.system_state['is_circulating'])
        self.assertTrue(self.controller.system_state['heater_power'] < self.controller.INITIAL_HEATER_POWER)
        print("✓ Hot temperature response correct")
        
        # Test normal temperature
        print("Testing normal temperature response...")
        self.controller.temp_out.read_temp = Mock(return_value=52.5)  # Within range
        time.sleep(2)  # Allow control loop to respond
        
        self.assertFalse(self.controller.system_state['is_circulating'])
        print("✓ Normal temperature response correct")

    def test_3_water_level_monitoring(self):
        """Test water level monitoring and alerts"""
        print("\nTest 3: Testing water level monitoring...")
        
        # Test normal water level
        print("Testing normal water level...")
        self.controller.water_sensor.get_water_percentage = Mock(return_value=50.0)
        self.controller.start_process({'target_temp': 52.5})
        time.sleep(1)
        
        self.assertFalse(self.controller.alerts['low_water'])
        print("✓ Normal water level correct")
        
        # Test low water warning
        print("Testing low water warning...")
        self.controller.water_sensor.get_water_percentage = Mock(return_value=9.0)
        time.sleep(6)  # Allow monitoring loop to update
        
        self.assertTrue(self.controller.alerts['low_water'])
        print("✓ Low water warning correct")
        
        # Test critical water level
        print("Testing critical water level...")
        self.controller.water_sensor.get_water_percentage = Mock(return_value=4.0)
        time.sleep(6)  # Allow monitoring loop to update
        
        self.assertFalse(self.controller.running)  # Should stop process
        print("✓ Critical water level response correct")

    def test_4_powder_level_monitoring(self):
        """Test powder level monitoring and alerts"""
        print("\nTest 4: Testing powder level monitoring...")
        
        # Test normal powder level
        print("Testing normal powder level...")
        self.controller.powder_sensor.get_powder_percentage = Mock(return_value=50.0)
        self.controller.start_process({'target_temp': 52.5})
        time.sleep(1)
        
        self.assertFalse(self.controller.alerts['low_powder'])
        print("✓ Normal powder level correct")
        
        # Test low powder warning
        print("Testing low powder warning...")
        self.controller.powder_sensor.get_powder_percentage = Mock(return_value=19.0)
        time.sleep(6)  # Allow monitoring loop to update
        
        self.assertTrue(self.controller.alerts['low_powder'])
        print("✓ Low powder warning correct")
        
        # Test critical powder level
        print("Testing critical powder level...")
        self.controller.powder_sensor.get_powder_percentage = Mock(return_value=9.0)
        time.sleep(6)  # Allow monitoring loop to update
        
        self.assertFalse(self.controller.running)  # Should stop process
        print("✓ Critical powder level response correct")

    def test_5_emergency_stop(self):
        """Test emergency stop functionality"""
        print("\nTest 5: Testing emergency stop...")
        
        # Start process
        self.controller.start_process({'target_temp': 52.5})
        self.assertTrue(self.controller.running)
        
        # Trigger emergency stop
        self.controller.emergency_stop_process()
        
        # Verify all systems stopped
        self.assertFalse(self.controller.running)
        self.assertTrue(self.controller.emergency_stop)
        self.assertEqual(self.controller.system_state['heater_power'], 0)
        self.assertEqual(self.controller.system_state['flow_rate'], 0)
        
        print("✓ Emergency stop functionality correct")

    def test_6_circulation_control(self):
        """Test water circulation control"""
        print("\nTest 6: Testing circulation control...")
        
        # Test circulation activation on low temperature
        print("Testing circulation on low temperature...")
        self.controller.temp_out.read_temp = Mock(return_value=40.0)
        self.controller.start_process({'target_temp': 52.5})
        time.sleep(2)
        
        self.assertTrue(self.controller.system_state['is_circulating'])
        print("✓ Circulation activation on low temperature correct")
        
        # Test circulation deactivation on normal temperature
        print("Testing circulation on normal temperature...")
        self.controller.temp_out.read_temp = Mock(return_value=52.5)
        time.sleep(2)
        
        self.assertFalse(self.controller.system_state['is_circulating'])
        print("✓ Circulation deactivation on normal temperature correct")

def run_tests():
    """Run all system tests"""
    # Configure logging for tests
    logging.basicConfig(level=logging.INFO)
    
    # Run tests
    unittest.main(argv=[''], verbosity=2, exit=False)

if __name__ == '__main__':
    run_tests()
