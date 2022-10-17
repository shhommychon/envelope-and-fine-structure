import numpy as np
import scipy.signal as sps

from .base import BaseEnvelopeAlgo


class InstantaneousRMS(BaseEnvelopeAlgo):
    """RMS approach envelope

    implemented by Cecilia Jarne
        - https://github.com/katejarne/Envelope_Code
    """
    def __init__(
        self,
        step_time_sec=1., window_size=512
    ):
        # len for the time serie segment [Seconds]
        self.step_time_sec = step_time_sec
        # window size for RMS
        self.window_size = window_size
    
    def window_rms(self, input_signal):
        a = np.power(input_signal, 2)
        window = (np.ones(self.window_size)/self.window_size).astype(np.float32)
        return np.sqrt(np.convolve(a, window, 'valid'))

    def _run(self, input_signal, sampling_rate, **kwargs):
        org_audio_len = input_signal.shape[0]
        
        step_time_sample = int(sampling_rate * self.step_time_sec)
        work_audio_len = 0
        while work_audio_len < org_audio_len:
            work_audio_len += step_time_sample
        work_audio_len += work_audio_len % self.window_size # for 'valid' operation
        
        whole_frame = np.zeros(work_audio_len, dtype=np.float32)
        whole_frame[:org_audio_len] = input_signal

        x       = sps.medfilt(sps.detrend(whole_frame, axis=-1, type='linear'))
        x_rms   = self.window_rms(x)

        envelope = x_rms[:org_audio_len]
        fine_structure = input_signal / envelope

        return envelope, fine_structure
