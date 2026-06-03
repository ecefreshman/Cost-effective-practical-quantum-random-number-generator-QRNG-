from time import sleep, ctime, localtime
import numpy as np
import pyaudio


def sample_variance(p, f, c, r, chunk, device, record_seconds):
    stream = p.open(format=f,
                    channels=c,
                    rate=r,
                    input=True,
                    frames_per_buffer=chunk,
                    input_device_index=device)
    collect = []
    for i in range(0, int(r / chunk * record_seconds)):
        data_b = stream.read(chunk)
        # collect sample results from left sound channel
        data_a = np.frombuffer(data_b, np.int16)[0::2]
        collect.append(data_a)
    stream.close()
    arr = np.array(collect)
    return np.mean(arr), np.var(arr)


# monitor parameters
monitor_time = 0.5    # unit: h
csv_filename = f"noise mean and variance in {monitor_time} hours-{localtime().tm_mon}{localtime().tm_mday}-{localtime().tm_hour}.csv"
period = 10    # unit: s
# record parameters
CHUNK = 512
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 48000
RECORD_SECONDS = 4
DEVICE = 1
p = pyaudio.PyAudio()
# list to reserve the sampled variance
print(csv_filename)
sample = []

for i in range(int(monitor_time * 3600 // period)):
    mean, var = sample_variance(p=p,
                                f=FORMAT,
                                c=CHANNELS,
                                r=RATE,
                                chunk=CHUNK,
                                device=DEVICE,
                                record_seconds=RECORD_SECONDS)
    print(f"{ctime()}, sample mean: {mean},\tvariance: {var}")
    sample.append(np.array([mean, var]))
    sleep(period - RECORD_SECONDS)

# last measure after the loop/interation
mean, var = sample_variance(p=p,
                            f=FORMAT,
                            c=CHANNELS,
                            r=RATE,
                            chunk=CHUNK,
                            device=DEVICE,
                            record_seconds=RECORD_SECONDS)
print(f"{ctime()}, sample mean: {mean},\tvariance: {var}")
sample.append(np.array([mean, var]))

p.terminate()
sample = np.array(sample)
np.savetxt(csv_filename, sample, delimiter=",", fmt="%f")
