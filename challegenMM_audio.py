import librosa
import numpy as np
import os
from pathlib import Path
#import easygui
from tkinter import messagebox
import lock
from pydub import AudioSegment

# variables globales
# ------------------
props_dict={} 
DEBUG_MODE=True

def init(props):
    global props_dict
    print("Python: Enter in init")
    
    #props es un diccionario
    props_dict= props

    # retornamos un cero como si fuese ok, porque
    # no vamos a ejecutar ahora el challenge
    return 0 # si init va mal retorna -1 else retorna 0

def executeChallenge():
    print("Starting execute")
    folder=os.environ['SECUREMIRROR_CAPTURES']
    print ("storage folder is :",folder)

    #mecanismo de lock BEGIN
    #-----------------------
    lock.lockIN("AUDIO")

    # pregunta si el usuario tiene movil con capacidad para grabar audio
    # -----------------------------------------------------
    #textos en español, aunque podrian ser parametros adicionales del challenge
    #conexion=easygui.ynbox('¿Tienes un movil con bluetooth activo y cámara emparejado con tu PC?',"challenge MM: RGB", choices=("Yes","Not"))
    conexion=messagebox.askyesno('challenge MM: RGB','¿Tienes un movil con bluetooth activo y emparejado a tu PC con capacidad para grabar un audio?')
    print(conexion)
    #Si el usuario responde que no ha emparejado móvil y PC, devolvemos clave y longitud 0
    if (conexion==False):
        lock.lockOUT("AUDIO")
        print ("return key zero and long zero")
        key=0
        key_size=0
        result =(key,key_size)
        print ("result:",result)
        return result # clave cero, longitud cero
  
    #popup msgbox pidiendo interaccion
    #---------------------------------
    #sent=easygui.ynbox(props_dict["interactionText"], "challenge MM: RGB", choices=("Yes","Not"))
    sent=conexion=messagebox.askyesno('challenge MM: RGB',props_dict['interactionText'])
    print(sent)

    #Si el usuario responde que no ha enviado la imagen, devolvemos clave y longitud 0
    if (sent== False):
        lock.lockOUT("AUDIO")
        print ("return key zero and long zero")
        key=0
        key_size=0
        result =(key,key_size)
        print ("result:",result)
        return result # clave cero, longitud cero
    
    # lectura del audio
    #-------------------------------
    # se supone que el usuario ha depositado un .wav usando bluetooth
    # el nombre del audio puede ser siempre el mismo, fijado por el proxy bluetooth.
    # aqui vamos a "forzar" el nombre del fichero para pruebas
      
    filename=folder+"/"+"capture.wav"
    filename_mp3=folder+"/"+"capture.mp3"
    filename_m4a=folder+"/"+"capture.m4a"
    filename_aac=folder+"/"+"capture.aac"
    converted_audio=folder+"/"+"converted_audio.wav"

    if (DEBUG_MODE==True):
        filename="test.wav"
        filename_mp3="nokia.mp3"
        filename_m4a="test.m4a"
        filename_aac="test.aac"
        converted_audio="converted_audio.wav"
        
    if os.path.exists(filename):
        print ("Fichero de captura",filename," encontrado")
        wav_data, sr = librosa.load(filename, sr=8000, mono=True)
        print(wav_data.shape)
        #mecanismo de lock END
        #-----------------------
        lock.lockOUT("AUDIO")

    elif os.path.exists(filename_mp3):
        print ("Fichero de captura",filename_mp3," encontrado")
        sound = AudioSegment.from_file(filename_mp3)
        sound.export(converted_audio, format="wav")
        wav_data, sr = librosa.load(converted_audio, sr=8000, mono=True)
        print(wav_data.shape)
        #mecanismo de lock END
        #-----------------------
        lock.lockOUT("AUDIO")

    elif os.path.exists(filename_m4a):
        print ("Fichero de captura",filename_m4a," encontrado")
        sound = AudioSegment.from_file(filename_m4a)
        sound.export(converted_audio, format="wav")
        wav_data, sr = librosa.load(converted_audio, sr=8000, mono=True)
        print(wav_data.shape)
        #mecanismo de lock END
        #-----------------------
        lock.lockOUT("AUDIO")

    elif os.path.exists(filename_aac):
        print ("Fichero de captura",filename_aac," encontrado")
        sound = AudioSegment.from_file(filename_aac)
        sound.export(converted_audio, format="wav")
        wav_data, sr = librosa.load(converted_audio, sr=8000, mono=True)
        print(wav_data.shape)
        #mecanismo de lock END
        #-----------------------
        lock.lockOUT("AUDIO")
        
    else:
        print ("ERROR: el fichero de captura",filename," no existe")
        key=0
        key_size=0
        result =(key,key_size)
        print ("result:",result)
        lock.lockOUT("AUDIO")
        return result # clave cero, longitud cero

    if (DEBUG_MODE==False):
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
        

    #construccion de la respuesta
    cad="%d"%(wav_data.shape)
    key = bytes(cad,'utf-8')
    key_size = len(key)
    result =(key, key_size)
    print ("result:",result)
    return result

    
if __name__ == "__main__":
    midict={"interactionText": '¿Has enviado el audio desde el móvil a tu PC?', "param2":3}
    init(midict)
    executeChallenge()
