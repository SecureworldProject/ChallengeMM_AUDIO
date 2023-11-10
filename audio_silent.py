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
        
    # Encontrar el índice del pico de frecuencia más prominente en cada frame
    indices_picos = np.argmax(espectrograma, axis=0)
    #print("indices_picos", indices_picos)
    # Convertir el índice del pico en frecuencia
    frecuencias = librosa.fft_frequencies(sr=sr)
    #print("frecuencias", frecuencias)
    # Obtener las frecuencias fundamentales correspondientes a los índices de pico
    frecuencias_fundamentales = frecuencias[indices_picos]
    #print("frecuencias_fundamentales", frecuencias_fundamentales)
    # Tomar la frecuencia fundamental promedio de todos los frames
    frecuencia_fundamental = 0
    c = 0
    for i in range(len(frecuencias_fundamentales)):
        if(frecuencias_fundamentales[i]>16000):
            m=int(frecuencias_fundamentales[i])
            print("m es:", m)
            if ((m>frecuencia_fundamental) & (c!=0)):
                if((m>16000) & (m<=16500)):
                    frecuencia_fundamental = 16
                elif((m>16500) & (m<=17500)):
                    frecuencia_fundamental = 17
                elif((m>17500) & (m<=18500)):
                    frecuencia_fundamental = 18
                elif((m>18500) & (m<=19500)):
                    frecuencia_fundamental = 19
                elif((m>19500) & (m<=20500)):
                    frecuencia_fundamental = 20
                elif((m>20500) & (m<=21500)):
                    frecuencia_fundamental = 21
                elif((m>21500) & (m<=22500)):
                    frecuencia_fundamental = 22

            c+=1

    print("Frecuencia fundamental:", frecuencia_fundamental, "kHz")
    return frecuencia_fundamental

def returnKey(frequency):
    if (frequency == 0):
        key = frequency
        key_size = 0
    else:
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
    RECORD_SECONDS = 3
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
    os.remove(filename)
    lock.lockOUT("Audio_Silent")
        
    # construccion de la respuesta
    return returnKey(f0)
    
if __name__ == "__main__":
    midict={}
    init(midict)
    executeChallenge()
