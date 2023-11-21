import librosa
import numpy as np
import os
from pathlib import Path
from tkinter import messagebox
import lock
from pydub import AudioSegment
import pyaudio
import wave

# variables globales
# ------------------
props_dict={} 
DEBUG_MODE=True
SAMPLING_RATE = 44100

def init(props):
    global props_dict
    print("Python: Enter in init")
    
    #props es un diccionario
    props_dict= props

    # retornamos un cero como si fuese ok, porque
    # no vamos a ejecutar ahora el challenge
    return 0 # si init va mal retorna -1 else retorna 0

def calculateF0(filename):
    #print("Fichero de captura", filename, " encontrado")
    wav_data, sr = librosa.load(filename, sr= SAMPLING_RATE, mono=True)
    
    # Calcular la STFT del audio
    espectrograma = np.abs(librosa.stft(wav_data))
    #print (  espectrograma.shape);
    #print (  espectrograma.shape[0]);
    
    # hay que anular las primeras 743 muestras del espectrograma para
    # hacer un filtro paso alto que borre las f< 16000 khz
    # porque shape es 1025,259 siendo 259 el numero de tramos de sonido con
    # 1025 frecuencias analizadas en cada intervalo
    # esto significa que en 1025 datos de frecuencia hay de 0 a 22050 hz
    # por lo tanto 16000 esta en la posicion 743
    num_frames=espectrograma.shape[1]
    numfreqs=espectrograma.shape[0]
    maxfrq=SAMPLING_RATE/2
    #print ("max f=", maxfrq)
    factor=numfreqs/maxfrq
    fpb=int(16000*factor)
    #print ("filtro de ",int(fpb))
    espectrograma[0:fpb][:]=0
        
    # Encontrar el índice del pico de frecuencia más prominente en cada frame
    indices_picos = np.argmax(espectrograma, axis=0)
    #print ("======================")
    #print(indices_picos)
    #print("indices_picos", indices_picos)
    # Convertir el índice del pico en frecuencia
    frecuencias = librosa.fft_frequencies(sr=sr)
    #print("frecuencias", frecuencias)
    # Obtener las frecuencias fundamentales correspondientes a los índices de pico
    frecuencias_fundamentales = frecuencias[indices_picos]
    #print ("---------------------------")
    #print(frecuencias_fundamentales);
    frecuencia_fundamental = int(np.mean(frecuencias_fundamentales))

    print("Frecuencia fundamental:", frecuencia_fundamental, "Hz")
    return frecuencia_fundamental

def returnKey(frequency):
    if (frequency == 0):
        key = frequency
        key_size = 0
    elif((frequency>16000) & (frequency<=16500)):
        frequency = 1
    elif((frequency>16500) & (frequency<=17000)):
        frequency = 2
    elif((frequency>17000) & (frequency<=17500)):
        frequency = 3
    elif((frequency>17500) & (frequency<=18000)):
        frequency = 4
    elif((frequency>18000) & (frequency<=18500)):
        frequency = 5
    elif((frequency>18500) & (frequency<=19000)):
        frequency = 6
    elif((frequency>19000) & (frequency<=19500)):
        frequency = 7
    elif((frequency>19500) & (frequency<=20000)):
        frequency = 8
    elif((frequency>20000) & (frequency<=20500)):
        frequency = 9
    elif((frequency>20500) & (frequency<=21000)):
        frequency = 10
    elif((frequency>21000) & (frequency<=21500)):
        frequency = 11
    elif((frequency>21500) & (frequency<=22000)):
        frequency = 12


    cad="%d"%(frequency)
    key = bytes(cad,'utf-8')
    key_size = len(key)
    result = (key, key_size)
    print ("result:",result)
    return result
    
def executeChallenge():
    print("Starting execute")
    dataPath=os.environ['SECUREMIRROR_CAPTURES']
    print ("storage folder is :",dataPath)

    #mecanismo de lock BEGIN
    lock.lockIN("Audio_Silent")

    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    CHUNK = 512
    RECORD_SECONDS = 4
    device_index = 2
    audio = pyaudio.PyAudio()
    
    info = audio.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')
    
    if (numdevices>0):
        
        print("comienza la grabación")
        stream = audio.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, input=True,input_device_index = 0,
                    frames_per_buffer=CHUNK)
        Recordframes = []
        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            Recordframes.append(data)
        
        stream.stop_stream()
        stream.close()
        audio.terminate()
        print("termino la grabación")
      
        
    else:
        messagebox.showinfo(message="Este challenge no se puede ejecutar porque no se encuentra micrófono en tu PC", title="No existe dispositivo de grabación de audio")
        lock.lockOUT("Audio_Silent")
        key_size = 0
        result = (NULL, key_size)
        print("CHALLENGE_Audio_Silent --> result:", result)
        return result

    
    #cerramos el lock
    lock.lockOUT("Audio_Silent")

    #Se crea el archivo de audio
    OUTPUT_FILENAME="capture.wav"
    WAVE_OUTPUT_FILENAME=os.path.join(dataPath+"\\",OUTPUT_FILENAME)
    waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    waveFile.setnchannels(CHANNELS)
    waveFile.setsampwidth(audio.get_sample_size(FORMAT))
    waveFile.setframerate(RATE)
    waveFile.writeframes(b''.join(Recordframes))
    waveFile.close()

    filename = os.path.join(dataPath, "capture.wav")

    f0 = calculateF0(filename)
    #os.remove(filename)
    lock.lockOUT("Audio_Silent")
        
    # construccion de la respuesta
    return returnKey(f0)
    
if __name__ == "__main__":
    midict={}
    init(midict)
    executeChallenge()
