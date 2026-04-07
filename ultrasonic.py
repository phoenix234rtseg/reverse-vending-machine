import lgpio
import time

TRIG = 23
ECHO = 24

h = lgpio.gpiochip_open(0)
lgpio.gpio_claim_output(h, TRIG)
lgpio.gpio_claim_input(h, ECHO)

print("Ultrasonic sensor started...")
time.sleep(2)

TIMEOUT = 0.02  # 20 ms

try:
    while True:
        # Trigger pulse
        lgpio.gpio_write(h, TRIG, 0)
        time.sleep(0.000002)
        lgpio.gpio_write(h, TRIG, 1)
        time.sleep(0.00001)
        lgpio.gpio_write(h, TRIG, 0)

        start_time = time.time()

        # Wait for echo HIGH
        while lgpio.gpio_read(h, ECHO) == 0:
            if time.time() - start_time > TIMEOUT:
                print("No echo received (check wiring)")
                break
            pulse_start = time.time()

        # Wait for echo LOW
        while lgpio.gpio_read(h, ECHO) == 1:
            if time.time() - pulse_start > TIMEOUT:
                print("Echo timeout")
                break
            pulse_end = time.time()

        if 'pulse_end' in locals():
            duration = pulse_end - pulse_start
            distance = round(duration * 17150, 2)
            print(f"Distance: {distance} cm")
            del pulse_end
        else:
            print("No valid distance")

        time.sleep(1)

except KeyboardInterrupt:
    print("Stopped by user")

finally:
    lgpio.gpiochip_close(h)

