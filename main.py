import re
from threading import Lock, Thread

import serial

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style

fig, ax = plt.subplots()

timestamp = list()
instant_noise = list()
smoothed_noise = list()

data_lock = Lock()


def main():
    interface = serial.Serial("/dev/ttyACM0", 115200, timeout=1)

    while True:
        new_line = interface.readline()
        result = re.search(r'\((\d+)\) IAVOZ_SYS: STP: (\d+.\d+) STP AVERAGE: (\d+) noise_level: (\d+.\d+)', str(new_line))

        if result is None:
            continue

        time = int(result.group(1))
        stp = float(result.group(2))
        stp_avg = int(result.group(3))
        noise_level = float(result.group(4))

        with data_lock:
            timestamp.append(time)
            instant_noise.append(stp)
            smoothed_noise.append(noise_level)
            # print(f'{xs=} {ys=}')

        # print(f'{timestamp=} {stp=}, {stp_avg=}, {noise_level=}')

    interface.close()


def animate(frame):
    global timestamp, instant_noise, smoothed_noise, data_lock
    max_samples = 200

    with data_lock:
        timestamp = timestamp[-max_samples:]
        instant_noise = instant_noise[-max_samples:]
        smoothed_noise = smoothed_noise[-max_samples:]

    # Draw x and y lists
    ax.clear()
    ax.plot(timestamp, instant_noise, color='b', label='instant noise')
    ax.plot(timestamp, smoothed_noise, color='r', label='smoothed noise')

    # Format plot
    plt.xticks(rotation=45, ha='right')
    plt.subplots_adjust(bottom=0.30)
    plt.title('Instant noise vs averaged noise')
    plt.ylabel('Temperature (deg C)')

    print(f'{frame=}: {timestamp}, {instant_noise}, {smoothed_noise}')

    return None


if __name__ == '__main__':
    my_thread = Thread(target=main, args=())
    my_thread.start()

    ani = animation.FuncAnimation(fig=fig, func=animate, interval=100)
    plt.show()
