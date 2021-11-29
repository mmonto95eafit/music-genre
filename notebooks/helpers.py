# ToDo: Add functions that we consider that are important

import librosa
import numpy as np


WINDOW_SIZE = 3
BEST_MODEL = '../data/models/toy_model.joblib'
MUSIC_GENRES = {0: 'blues',
                1: 'classical',
                2: 'country',
                3: 'disco',
                4: 'hiphop',
                5: 'jazz',
                6: 'metal',
                7: 'pop',
                8: 'reggae',
                9: 'rock'}


def extract_features(window):
    chromogram = librosa.feature.chroma_stft(window)
    rms = librosa.feature.rms(window)
    centroid = librosa.feature.spectral_centroid(window)
    bandwidth = librosa.feature.spectral_bandwidth(window)
    roll_off = librosa.feature.spectral_rolloff(window)
    zero_crossing_rate = librosa.feature.zero_crossing_rate(window)
    harmony, perceptual = librosa.effects.hpss(window)
    tempo, _ = librosa.beat.beat_track(window)
    mfcc = librosa.feature.mfcc(window)

    mfcc_values = []
    for mean, var in zip(mfcc.mean(axis=1), np.var(mfcc, axis=1)):
        mfcc_values.append(mean)
        mfcc_values.append(var)

    return [
        chromogram.mean(),
        np.var(chromogram),
        rms.mean(),
        np.var(rms),
        centroid.mean(),
        np.var(centroid),
        bandwidth.mean(),
        np.var(bandwidth),
        roll_off.mean(),
        np.var(roll_off),
        zero_crossing_rate.mean(),
        np.var(zero_crossing_rate),
        harmony.mean(),
        np.var(harmony),
        perceptual.mean(),
        np.var(perceptual),
        tempo,
        *mfcc_values
    ]
