import numpy as np
import scipy.signal as sps

from .base import BaseEnvelopeAlgo


class DirectPeakDetection(BaseEnvelopeAlgo):
    """A direct peak detection

    proposed and implemented by Cecilia Jarne
        - https://github.com/katejarne/Envelope_Code
    """
    def __init__(
        self,
        step_time_sec=1., freq_cut=300, interval_length=35
    ):
        # len for the time serie segment [Seconds]
        self.step_time_sec = step_time_sec
        # Frecuency cut for the Jarne's envelope calculation [Hz]
        self.freq_cut = freq_cut

        # change this number depending on your signal frequency content and time scale
        self.interval_length = interval_length

    def get_envelope(self, input_signal):
        # Taking the absolute value
        absolute_signal = np.abs(input_signal)
        output_signal = np.zeros(input_signal.shape[0], dtype=np.float32)

        # Peak detection
        for base_index in range(0, absolute_signal.shape[0]):
            lookback_index = max(base_index - (self.interval_length-1), 0)
            maximum = np.max(absolute_signal[lookback_index:base_index+1])
            output_signal[base_index] = maximum

        return output_signal

    def _run(self, input_signal, sampling_rate, **kwargs):
        org_audio_len = input_signal.shape[0]
        
        step_time_sample = int(sampling_rate * self.step_time_sec)
        work_audio_len = 0
        while work_audio_len < org_audio_len:
            work_audio_len += step_time_sample
        
        whole_frame = np.zeros(work_audio_len, dtype=np.float32)

        # Filter definition for Low Pass Frequency
        W       = float(self.freq_cut/sampling_rate)    # filter parameter cut frequency over the sample frequency
        b, a    = sps.butter(4, W, btype='lowpass')     # Numerator (b) and denominator (a) polynomials of the IIR filter

        for step in range(0, work_audio_len, step_time_sample):
            if step == 0:
                input_stepframe = input_signal[step:step+step_time_sample]
                env_stepframe = self.get_envelope(input_stepframe)
            else:
                input_stepframe = input_signal[step-self.interval_length:step+step_time_sample]
                env_stepframe = self.get_envelope(input_stepframe)[self.interval_length:]

            filtered_env = sps.filtfilt(b, a, env_stepframe)
            whole_frame[step:step+filtered_env.shape[0]] = filtered_env[:filtered_env.shape[0]]

        envelope = whole_frame[:org_audio_len]
        fine_structure = input_signal / envelope

        return envelope, fine_structure
