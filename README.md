# ChallengeMM_AUDIO
Este challenge obtiene la frecuencia fundamental de un audio dado.


# DESCRIPCION y FIABILIDAD
AUDIO es un challenge que pide al usuario hacer una grabación de sonido o seleccionar un audio determinado
el challenge obtiene la frecuencia fundamental (f0) de este audio.

# FUNCIONAMIENTO:
Retorna la frecuencia fundamental del audio.

# REQUISITOS:
La variable de entorno **SECUREMIRROR_CAPTURES** debe existir y apuntar al path donde el server bluetooth deposita las capturas
el fichero de captura se debe llamar "capture" y tener una extessión de tipo audio: .wav, .mp3, .m4a, .aac.

Hay una variable en el challenge  llamada **"DEBUG_MODE"**

ejemplo configuracion json
```json
{
"FileName": "challenge_loader_python.dll",
"Description": "challenge que calcula la frecuencia fundamental de un audio",
"Props": {
  "module_python": "challegenMM_audio",
  "validity_time": 3600,
  "refresh_time": 1000,
  "interactionText": "¿Has enviado el audio desde el móvil a tu PC?",
},
"Requirements": "recorder" 
}
```
