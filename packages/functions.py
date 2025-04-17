import json

async def mensaje_spam_validacion(mensaje: str)-> bool:
    retorno = False
    emojis = 0
    if(not mensaje.replace(" ","").isalpha()):
        for letra in mensaje:
            if(ord(letra) > 255):
                emojis += 1
        
        retorno = True if emojis >= 5 else False
    
    if(emojis <= 5):
        contador = 0
        auxiliar = ""
        for i in range(len(mensaje)):
            if(i == 0):
                auxiliar = mensaje[i]
            elif(mensaje[i] == auxiliar):
                contador += 1
            auxiliar = mensaje[i]
        
        retorno = True if contador >= 5 else False
    
    return retorno

async def agregar_seguidor(nombre: str)->bool | str:
    retorno = True
    try:
        with open("/root/tiktoklive/jsons/seguidos_dia.json", "r", encoding="utf-8") as archivo:
            try:
                datos = json.load(archivo)
                if(datos.get(nombre)):
                    return nombre
            except:
                datos = {}
        
        with open("/root/tiktoklive/jsons/seguidos_dia.json", "w", encoding="utf-8") as archivo:
            datos[nombre] = True
            json.dump(datos, archivo, indent=4)
    except:
        retorno = False
    
    return retorno

async def reiniciar_lista():
    with open("/root/tiktoklive/jsons/seguidos_dia.json", "w", encoding="utf-8") as archivo:
        json.dump({},archivo)