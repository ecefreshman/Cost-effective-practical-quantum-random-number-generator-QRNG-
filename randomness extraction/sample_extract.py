from time import ctime
import pyaudio
import numpy as np
# import wave
# import sounddevice as sd

CHUNK = 256
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 48000
RECORD_SECONDS = 3600
file_name = "extracted bits-1.csv"

# collect = []
secret_bits = []

n = CHUNK * 16   # length of input bit strings
m = 646          # length of output (adjudicative according to the requirement, <= n)

# ---------- construct Toeplitz seeds (m + n - 1 bits) ----------
conv_len = m + n - 1
seed = np.random.randint(0, 2, conv_len)

# ---------- linear convolution with FFT  ----------
# see the reference of example_program.py
fft_len = 1 << (conv_len - 1).bit_length()


try:
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK,
                    input_device_index=1)
    print(ctime())
    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data_b = stream.read(CHUNK)
        data_a = np.frombuffer(data_b, np.int16)[0::2]
        # collect.append(data_a)
        # all = np.hstack((all, data_a))
        # x_input = np.loadtxt("record_audio.csv", delimiter=",", dtype=np.int16)[492]

        # translate 256 numbers of np.int16 into 2^12 single bits
        x_uint16 = data_a.astype(np.uint16)
        # bits_per_sample shape: (256, 16), listed as MSB -> LSB
        bits_per_sample = ((x_uint16[:, None] >> np.arange(15, -1, -1)) & 1).astype(np.uint8)
        x_bits = bits_per_sample.reshape(-1)

        fa = np.fft.rfft(seed.astype(np.float64), n=fft_len)
        fb = np.fft.rfft(x_bits.astype(np.float64), n=fft_len)
        conv = np.fft.irfft(fa * fb, n=fft_len)[:conv_len]

        # keep first m items and mod 2
        y_bits = (np.rint(conv[:m]).astype(np.int64) & 1).astype(np.uint8)

        secret_bits.append(y_bits)

        stream.close()
        p.terminate()

except Exception as e:
    print(e)
finally:
    print(ctime())
    # arr_1 = np.array(collect)
    arr_2 = np.array(secret_bits)
    # np.savetxt("original_sample.csv", arr_1, delimiter=",", fmt="%d")
    np.savetxt(file_name, arr_2, delimiter=",", fmt="%d")

    print("Random bits are extracted.")
    print(arr_2.shape)
