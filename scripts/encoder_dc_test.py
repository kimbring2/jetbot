import Jetson.GPIO as GPIO
import time

# Pin Definitions (BOARD numbering)
LEFT_ENCODER_A = 31
LEFT_ENCODER_B = 29
RIGHT_ENCODER_A = 32
RIGHT_ENCODER_B = 33

class MotorEncoder:
    def __init__(self, pin_a, pin_b, label):
        self.pin_a = pin_a
        self.pin_b = pin_b
        self.label = label
        self.position = 0
        
        # Setup pins
        GPIO.setup(self.pin_a, GPIO.IN)
        GPIO.setup(self.pin_b, GPIO.IN)
        
        # Attach interrupt
        GPIO.add_event_detect(self.pin_a, GPIO.BOTH, callback=self._callback)

    def _callback(self, channel):
        # Read states to determine direction
        a_state = GPIO.input(self.pin_a)
        b_state = GPIO.input(self.pin_b)
        
        if a_state == b_state:
            self.position += 1
        else:
            self.position -= 1

def main():
    # GPIO Setup
    GPIO.setmode(GPIO.BOARD)
    
    # Initialize Left and Right Encoders
    left_motor = MotorEncoder(LEFT_ENCODER_A, LEFT_ENCODER_B, "Left")
    right_motor = MotorEncoder(RIGHT_ENCODER_A, RIGHT_ENCODER_B, "Right")
    
    print("Reading dual encoders... Press Ctrl+C to stop.")
    
    try:
        while True:
            print(f"L: {left_motor.position} | R: {right_motor.position}    ", end='\r')
            time.sleep(0.05)
    except KeyboardInterrupt:
        print("\nCleaning up...")
    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    main()