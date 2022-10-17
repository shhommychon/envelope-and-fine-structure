import numpy as np
import scipy.signal as sps

from .base import BaseEnvelopeAlgo


class EnvelopeFollower(BaseEnvelopeAlgo):
    """Low-pass Filter envelope

    implemented by Cecilia Jarne
        - https://github.com/katejarne/Envelope_Code
    """
    def __init__(
        self,
        step_time_sec=1., freq_cut=150
    ):
        # len for the time serie segment [Seconds]
        self.step_time_sec = step_time_sec
        # Frecuency cut for the low-pass envelope [Hz]
        self.freq_cut = freq_cut

    def _run(self, input_signal, sampling_rate, **kwargs):
        org_audio_len = input_signal.shape[0]
        
        step_time_sample = int(sampling_rate * self.step_time_sec)
        work_audio_len = 0
        while work_audio_len < org_audio_len:
            work_audio_len += step_time_sample
        
        whole_frame = np.zeros(work_audio_len, dtype=np.float32)

        # Filter definition for Low Pass Frequency
        W       = float(self.freq_cut/sampling_rate)    # filter parameter cut frequency over the sample frequency
        b, a    = sps.butter(1, W, btype='lowpass')     # Numerator (b) and denominator (a) polynomials of the IIR filter
        
        x       = sps.medfilt(sps.detrend(input_signal, axis=-1, type='linear'))

        for step in range(0, work_audio_len, step_time_sample):
            input_stepframe = x[step:step+step_time_sample]

            # envelope low pass
            filtered = sps.filtfilt(b, a, np.abs(input_stepframe))
            whole_frame[step:step+filtered.shape[0]] = filtered[:filtered.shape[0]]

        envelope = whole_frame[:org_audio_len]
        fine_structure = input_signal / envelope

        return envelope, fine_structure
