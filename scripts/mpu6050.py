import math
import time
import Adafruit_GPIO.I2C as I2C

# MPU-6050 Constants
MPU6050_ADDR = 0x68
PWR_MGMT_1   = 0x6B

class KalmanFilter:
    def __init__(self):
        self.Q_angle = 0.001
        self.Q_bias = 0.003
        self.R_measure = 0.03
        self.angle = 0.0
        self.bias = 0.0
        self.P = [[0, 0], [0, 0]]

    def get_angle(self, new_angle, new_rate, dt):
        rate = new_rate - self.bias
        self.angle += dt * rate
        self.P[0][0] += dt * (dt * self.P[1][1] - self.P[0][1] - self.P[1][0] + self.Q_angle)
        self.P[0][1] -= dt * self.P[1][1]
        self.P[1][0] -= dt * self.P[1][1]
        self.P[1][1] += self.Q_bias * dt

        y = new_angle - self.angle
        S = self.P[0][0] + self.R_measure
        K = [self.P[0][0] / S, self.P[1][0] / S]

        self.angle += K[0] * y
        self.bias += K[1] * y
        
        P00_temp = self.P[0][0]
        P01_temp = self.P[0][1]
        self.P[0][0] -= K[0] * P00_temp
        self.P[0][1] -= K[0] * P01_temp
        self.P[1][0] -= K[1] * P00_temp
        self.P[1][1] -= K[1] * P01_temp
        return self.angle

# Initialize I2C using Adafruit_GPIO
i2c = I2C.get_i2c_device(MPU6050_ADDR, busnum=7)

def read_raw_data(addr):
    # MPU-6050 provides 16-bit values in two 8-bit registers (High and Low)
    high = i2c.readU8(addr)
    low = i2c.readU8(addr + 1)
    value = (high << 8) | low
    if value > 32768: # Convert to signed 16-bit
        value = value - 65536
    return value

# Wake up MPU-6050
i2c.write8(PWR_MGMT_1, 0)

yaw = 0.0
kalman_pitch = KalmanFilter()
kalman_roll  = KalmanFilter()
last_time = time.time()

print("Kalman Filter active. Balancing logic ready...")

try:
    while True:
        curr_time = time.time()
        dt = curr_time - last_time
        last_time = curr_time

        # Read Accelerometer
        ax = read_raw_data(0x3B)
        ay = read_raw_data(0x3D)
        az = read_raw_data(0x3F)

        # Read Gyroscope (Scale factor 131.0 for +/- 250 deg/s)
        gx = read_raw_data(0x43) / 131.0
        gy = read_raw_data(0x45) / 131.0
        gz = read_raw_data(0x47) / 131.0

        # PITCH (Tilt): Accelerometer + Gyro fusion
        accel_pitch = math.degrees(math.atan2(ay, az))
        pitch = kalman_pitch.get_angle(accel_pitch, gy, dt)

        # 2. ROLL (Around X-axis)
        accel_roll = math.degrees(math.atan2(ax, az))
        roll = kalman_roll.get_angle(accel_roll, gx, dt)
        
        # YAW (Heading): Pure Gyro integration
        # Since MPU6050 has no magnetometer, we assume the initial yaw is 0.
        yaw += gz * dt 

        # Print data formatted for readability
        print(f"P: {pitch:6.1f}° | R: {roll:6.1f}° | Y: {yaw:6.1f}°", end='\r')
        time.sleep(0.01)

except KeyboardInterrupt:
    print("\nStopping...")