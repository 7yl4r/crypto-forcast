import luigi

import config
from common.analyze.FFT import FFT
from btc.preprocess.Resample2DailyInterpolated import Resample2DailyInterpolated

class BTCFFT(FFT):
    def requires(self):
        return [
            Resample2DailyInterpolated()
        ]

    def output(self):
        return [
            luigi.LocalTarget(config.data_dir+"/analyze/btc_fft.png")
        ]

    col_names=['date','price']
