import lgpio
import time

IR_PIN = 17  # change if needed

h = lgpio.gpiochip_open(0)
lgpio.gpio_claim_input(h, IR_PIN)

print("IR sensor started...")

try:
    while True:
        value = lgpio.gpio_read(h, IR_PIN)

        if value == 0:
            print("Object detected 🚨")
        else:
            print("No object")

        time.sleep(0.5)

except KeyboardInterrupt:
    print("Stopped by user")

finally:
    lgpio.gpiochip_close(h)
