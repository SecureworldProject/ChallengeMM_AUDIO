import librosa
import numpy as np
import os
from tkinter import messagebox
import lock
from pydub import AudioSegment

# variables globales
# ------------------
props_dict = {}
DEBUG_MODE = True
SAMPLING_RATE = 44100
interval = 50


def init(props):
    global props_dict
    print("Python: Enter in init")
    # props es un diccionario
    props_dict = props

    # retornamos un cero como si fuese ok, porque
    # no vamos a ejecutar ahora el challenge
    # si init va mal retorna -1 else retorna 0
    return 0


def calculateF0(filename):
    wav_data, sr = librosa.load(filename, sr=SAMPLING_RATE, mono=True)

    # Calcular la STFT del audio
    espectrograma = np.abs(librosa.stft(wav_data))

    # hay que anular las primeras 743 muestras del espectrograma para
    # hacer un filtro paso alto que borre las f< 16000 khz
    # porque shape es 1025,259 siendo 259 el numero de tramos de sonido con
    # 1025 frecuencias analizadas en cada intervalo
    # esto significa que en 1025 datos de frecuencia hay de 0 a 22050 hz
    # por lo tanto 16000 esta en la posicion 743

    numfreqs = espectrograma.shape[0]
    maxfrq = SAMPLING_RATE / 2
    # print ("max f=", maxfrq)
    factor = numfreqs / maxfrq
    fpb = int(16000 * factor)
    # print ("filtro de ",int(fpb))
    espectrograma[0:fpb][:] = 0

    # Encontrar el índice del pico de frecuencia más prominente en cada frame
    indices_picos = np.argmax(espectrograma, axis=0)

    # Convertir el índice del pico en frecuencia
    frecuencias = librosa.fft_frequencies(sr=sr)

    # Obtener las frecuencias fundamentales correspondientes a los índices de pico
    frecuencias_fundamentales = frecuencias[indices_picos]

    # Tomar la frecuencia fundamental promedio de todos los frames
    frecuencia_fundamental = np.mean(frecuencias_fundamentales)

    print("Frecuencia fundamental:", frecuencia_fundamental, "Hz")
    return frecuencia_fundamental


def returnKey(frequency, interval):
    if (frequency == 0):
        key = frequency
        key_size = 0
    else:
        frequency = (frequency - 16000) // interval + 1
        cad = "%d" % (frequency)
        key = bytes(cad, 'utf-8')
        key_size = len(key)
    result = (key, key_size)
    print("result:", result)
    return result


def fundamentalFrequency(filename, filename_mp3, filename_m4a, filename_aac, converted_audio):
    if os.path.exists(filename):
        f0 = calculateF0(filename)
        return f0

        # mecanismo de lock END
        lock.lockOUT("AUDIO")

    elif os.path.exists(filename_mp3):
        print("Fichero de captura", filename_mp3, " encontrado")
        sound = AudioSegment.from_file(filename_mp3)
        sound.export(converted_audio, format="wav")

        f0 = calculateF0(converted_audio)
        lock.lockOUT("AUDIO")
        return f0

    elif os.path.exists(filename_m4a):
        print("Fichero de captura", filename_m4a, " encontrado")
        sound = AudioSegment.from_file(filename_m4a)
        sound.export(converted_audio, format="wav")
        f0 = calculateF0(converted_audio)
        lock.lockOUT("AUDIO")
        return f0

    elif os.path.exists(filename_aac):
        print("Fichero de captura", filename_aac, " encontrado")
        sound = AudioSegment.from_file(filename_aac)
        sound.export(converted_audio, format="wav")

        f0 = calculateF0(converted_audio)
        lock.lockOUT("AUDIO")
        return f0

    else:
        print("ERROR: el fichero de captura", filename, " no existe")
        lock.lockOUT("AUDIO")
        return 0


def executeChallenge():
    print("Starting execute")
    folder = os.environ['SECUREMIRROR_CAPTURES']
    print("storage folder is :", folder)

    # mecanismo de lock BEGIN
    lock.lockIN("AUDIO")

    # lectura del audio
    # -------------------------------
    # se supone que el usuario ha depositado un .wav usando bluetooth
    # el nombre del audio puede ser siempre el mismo, fijado por el proxy bluetooth.
    # aqui vamos a "forzar" el nombre del fichero para pruebas

    filename = os.path.join(folder, "capture.wav")
    filename_mp3 = os.path.join(folder, "capture.mp3")
    filename_m4a = os.path.join(folder, "capture.m4a")
    filename_aac = os.path.join(folder, "capture.aac")
    converted_audio = os.path.join(folder, "converted_audio.wav")

    if (DEBUG_MODE):
        filename = "test.wav"
        filename_mp3 = "test.mp3"
        filename_m4a = "test.m4a"
        filename_aac = "test.aac"
        converted_audio = "converted_audio.wav"

        f0 = fundamentalFrequency(filename, filename_mp3, filename_m4a, filename_aac, converted_audio)

    else:
        # pregunta si el usuario tiene movil con capacidad para grabar audio
        conexion = messagebox.askyesno('challenge MM: AUDIO', '¿Tienes un movil con bluetooth activo y emparejado a tu PC con capacidad para grabar un audio?')
        print(conexion)

        # Si el usuario responde que no ha emparejado móvil y PC, devolvemos clave y longitud 0
        if (conexion is False):
            print("ERROR: el móvil no se ha emparejado")
            lock.lockOUT("AUDIO")
            return returnKey(0)
        else:
            # popup msgbox pidiendo interaccion
            sent = messagebox.askyesno('challenge MM: AUDIO', props_dict['interactionText'])
            print(sent)

            # Si el usuario responde que no ha enviado la imagen, devolvemos clave y longitud 0
            if (sent is False):
                print("ERROR: la imagen no se ha enviado")
                lock.lockOUT("AUDIO")
                return returnKey(0)

            else:
                f0 = fundamentalFrequency(filename, filename_mp3, filename_m4a, filename_aac, converted_audio)
                if os.path.exists(filename):
                    os.remove(filename)
                if os.path.exists(filename_mp3):
                    os.remove(filename_mp3)
                if os.path.exists(filename_m4a):
                    os.remove(filename_m4a)
                if os.path.exists(filename_aac):
                    os.remove(filename_aac)
                if os.path.exists(converted_audio):
                    os.remove(converted_audio)

    # construccion de la respuesta
    return returnKey(f0, interval)


if __name__ == "__main__":
    midict = {"interactionText": '¿Has enviado el audio desde el móvil a tu PC?', "param2": 3}
    init(midict)
    executeChallenge()
