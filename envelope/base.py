import os

from scipy.io.wavfile import read


class BaseEnvelopeAlgo(object):
    def __init__(self):
        pass

    def read_wav(self, wav_path):
        sampling_rate, data = read(wav_path)
        if len(data.shape) == 2:
            assert data.shape[1] == 2
            data = data[:, 0]
        return sampling_rate, data

    def _run(self, *args, **kwargs):
        raise NotImplementedError

    def __call__(self, input_signal, sampling_rate=None, **kwargs):
        if type(input_signal) is str:
            # input_signal에 파일 경로를 넣은 경우
            assert os.path.isfile(input_signal), input_signal
            sampling_rate, input_signal = self.read_wav(input_signal)
        else:
            # input_signal에 음원 데이터 array를 넣은 경우
            assert sampling_rate is not None

        envelope, fine_structure = self._run(input_signal, sampling_rate, **kwargs)

        return envelope, fine_structure
