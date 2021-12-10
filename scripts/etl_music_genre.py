import pandas as pd
import numpy as np
import librosa.display
import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
import boto3


# @params: [JOB_NAME]
args = getResolvedOptions(sys.argv, ['JOB_NAME'])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Librerias


data_dir = 's3://musicgenredatalake/raw/songs/'

genres = ['blues', 'classical', 'country', 'disco',
          'hiphop', 'jazz', 'metal', 'pop', 'reggae', 'rock']
window_size = 3

columns = ['filename', 'length', 'chroma_stft_mean', 'chroma_stft_var', 'rms_mean',
           'rms_var', 'spectral_centroid_mean', 'spectral_centroid_var',
           'spectral_bandwidth_mean', 'spectral_bandwidth_var', 'rolloff_mean',
           'rolloff_var', 'zero_crossing_rate_mean', 'zero_crossing_rate_var',
           'harmony_mean', 'harmony_var', 'perceptr_mean', 'perceptr_var', 'tempo',
           'mfcc1_mean', 'mfcc1_var', 'mfcc2_mean', 'mfcc2_var', 'mfcc3_mean',
           'mfcc3_var', 'mfcc4_mean', 'mfcc4_var', 'mfcc5_mean', 'mfcc5_var',
           'mfcc6_mean', 'mfcc6_var', 'mfcc7_mean', 'mfcc7_var', 'mfcc8_mean',
           'mfcc8_var', 'mfcc9_mean', 'mfcc9_var', 'mfcc10_mean', 'mfcc10_var',
           'mfcc11_mean', 'mfcc11_var', 'mfcc12_mean', 'mfcc12_var', 'mfcc13_mean',
           'mfcc13_var', 'mfcc14_mean', 'mfcc14_var', 'mfcc15_mean', 'mfcc15_var',
           'mfcc16_mean', 'mfcc16_var', 'mfcc17_mean', 'mfcc17_var', 'mfcc18_mean',
           'mfcc18_var', 'mfcc19_mean', 'mfcc19_var', 'mfcc20_mean', 'mfcc20_var', 'label']


def extract_features(window):
    ''' Pendiente documentar '''

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


bucket = 's3://musicgenredatalake/raw/songs/'

client = boto3.client('s3')
paginator = client.get_paginator('list_objects_v2')
features = []
for genre in genres:
    page_iterator = paginator.paginate(Bucket=bucket+f'{genre}')
    for file in page_iterator:
        try:
            signal, sample_rate = librosa.load(f'{data_dir}/{genre}/{file}')
            # Get rid of silence at the begining and end
            signal, _ = librosa.effects.trim(signal)
            n_points = window_size * sample_rate
            for i in range(int(len(signal) / n_points)):
                print(genre, file, i, end='\r')
                window = signal[i * n_points:(i + 1) * n_points]
                if len(window):
                    values = extract_features(window)
                    values = [file.replace('.wav', f'.{i}.wav'), len(
                        window), *values, genre]
                    features.append(values)
        except Exception as ex:
            print(ex)

df = pd.DataFrame(features)
df.columns = columns
print(df)
