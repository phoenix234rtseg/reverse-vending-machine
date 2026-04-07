import time
import serial

ser = serial.Serial("/dev/ttyAMA0", 115200)

# === CONFIGURATION ===
SENSOR_HEIGHT = 40          # cm (sensor to conveyor belt)
EMPTY_DISTANCE = 40         # cm (no bottle)
THRESHOLD = 5               # cm tolerance

# Bottle height thresholds (cm)
HALF_LITER_MIN = 16
HALF_LITER_MAX = 23

FULL_LITER_MIN = 24
FULL_LITER_MAX = 32

bottle_detected = False
start_time = 0
min_distance = SENSOR_HEIGHT

def classify_bottle(height):
    if HALF_LITER_MIN <= height <= HALF_LITER_MAX:
        return "500 ml (Half Liter)"
    elif FULL_LITER_MIN <= height <= FULL_LITER_MAX:
        return "1 Liter (Full Bottle)"
    else:
        return "Unknown / Crushed Bottle"

def read_data():
    global bottle_detected, start_time, min_distance

    while True:
        if ser.in_waiting >= 9:
            data = ser.read(9)

            if data[0] == 0x59 and data[1] == 0x59:
                distance = data[2] + data[3] * 256

                # Bottle detected
                if distance < (EMPTY_DISTANCE - THRESHOLD):
                    if not bottle_detected:
                        bottle_detected = True
                        start_time = time.time()
                        min_distance = distance

                    min_distance = min(min_distance, distance)

                # Bottle passed
                else:
                    if bottle_detected:
                        end_time = time.time()
                        duration = end_time - start_time

                        bottle_height = SENSOR_HEIGHT - min_distance
                        bottle_type = classify_bottle(bottle_height)

                        print("\n--- Bottle Detected ---")
                        print(f"Height       : {bottle_height:.1f} cm")
                        print(f"Time on belt : {duration:.2f} s")
                        print(f"Type         : {bottle_type}")
                        print("-----------------------")

                        bottle_detected = False

                time.sleep(0.01)

if __name__ == "__main__":
    try:
        read_data()
    except KeyboardInterrupt:
        ser.close()
        print("Program stopped")



