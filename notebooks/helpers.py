# ToDo: Add functions that we consider that are important

#import librosa
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split


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


def mahalanobis(x, data, cov):
    x_mu = x - np.mean(data)
    inv_cov = np.linalg.inv(cov)
    mahalanobis_distances = np.diag(np.dot((x_mu @ inv_cov), x_mu.T))

    return mahalanobis_distances


def get_datasets(data_path='../data/features_3_sec.csv'):
    df = pd.read_csv(data_path)
    df['label'] = df['label'].astype('category')
    df['length'] = pd.to_numeric(df['length'])
    ##################
    df_x = df.drop(['filename', 'label', 'length'], axis=1)
    x = np.array(df_x)
    y = df['label'].cat.codes.values
    #########################
    df_x_cf = df_x.drop(
        ['spectral_centroid_mean', 'spectral_bandwidth_mean', 'rolloff_mean'], axis=1)
    x_cf = np.array(df_x_cf)
    y_cf = y
    #######################################

    scaler = MinMaxScaler()
    x_scaled = scaler.fit_transform(
        df.loc[:, 'chroma_stft_mean':'mfcc20_var'].values)
    y = df['label'].cat.codes.values

    cov = pd.read_csv('../data/kur_covariance_scaled.csv', header=None).values

    v = x_scaled - x_scaled.mean(axis=0)
    mahalanobis_distances = np.diag(v @ np.linalg.inv(cov) @ v.T)
    p25 = np.percentile(mahalanobis_distances, 25)
    p75 = np.percentile(mahalanobis_distances, 75)
    threshold = p75 + 3 * (p75 - p25)
    x_filtered = x_scaled[mahalanobis_distances < threshold]
    y_filtered = y[mahalanobis_distances < threshold]

    cols = df_x.columns
    df_x_filtered = pd.DataFrame(x_filtered, columns=cols)
    df_x_filtered_cf = df_x_filtered.drop(
        ['spectral_centroid_mean', 'spectral_bandwidth_mean', 'rolloff_mean'], axis=1)
    x_filtered_cf = np.array(df_x_filtered_cf)
    y_filtered_cf = y_filtered

    return (
        *train_test_split(x, y, random_state=42),
        *train_test_split(x_cf, y_cf, random_state=42),
        *train_test_split(x_filtered, y_filtered, random_state=42),
        *train_test_split(x_filtered_cf, y_filtered_cf, random_state=42),
    )
