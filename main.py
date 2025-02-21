import discord
import asyncio
from token_bot import TOKEN_BOT
from discord.ext import commands
from discord import FFmpegPCMAudio
from colorama import Fore,Style
from TikTokLive import TikTokLiveClient
from TikTokLive.events import ConnectEvent,CommentEvent,FollowEvent,GiftEvent
from gtts import gTTS
from packages.functions import mensaje_spam_validacion

cliente = TikTokLiveClient(unique_id="@elfokinronz")

intents = discord.Intents.default()
# permisos para que el bot puedae saber sobre miembros,mensajes y manejar canales
intents.members = True
intents.message_content = True
intents.voice_states = True

voice_client = None # establecemos en none para que cuando se conecte a un voice se cambie solo
audio_queue = asyncio.Queue()
alerta_follow = False
alerta_donacion = False

async def reproducir_comentarios():
    global voice_client # usamos la variable global
    global alerta_follow
    global alerta_donacion

    while(True): # un bucle para poder reproducir todos los comentarios
        texto = await audio_queue.get() # sacamos el texto de la cola
        if(voice_client and not voice_client.is_playing()): # validacion para saber que tengamos el voice activo y no este leyendo comentarios
            # generamos el mp3
            mensaje = gTTS(texto.lower(), lang="es")
            mensaje.save("sounds/mensaje.mp3")
            # reproducimos el audio
            audio = FFmpegPCMAudio("sounds/mensaje.mp3")
            voice_client.play(audio)

            while(voice_client.is_playing()): # si se esta reproduciendo agregamos un delay
                await asyncio.sleep(1)
            
            if(alerta_follow):
                audio_alerta = FFmpegPCMAudio("sounds/oye-gela.mp3")
                voice_client.play(audio_alerta)

                while(voice_client.is_playing()): # si se esta reproduciendo agregamos un delay
                    await asyncio.sleep(1)
                
                alerta_follow = False
            
            if(alerta_donacion):
                audio_alerta = FFmpegPCMAudio("sounds/goku-eta-vaina-e-seria.mp3")
                voice_client.play(audio_alerta)
                
                while(voice_client.is_playing()): # si se esta reproduciendo agregamos un delay
                    await asyncio.sleep(1)
                
                alerta_donacion = False

@cliente.on(ConnectEvent)
async def conectar_live(event: ConnectEvent)-> None:
    print(f"[+] Se conecto al Live de: {event.unique_id} correctamente!")

@cliente.on(CommentEvent)
async def leer_comentarios(event: CommentEvent)-> None:
    print(Fore.LIGHTYELLOW_EX + f"[Comentario] @{event.user.nickname} ha dicho: {event.comment}" + Style.RESET_ALL)
    comentario = event.comment
    mensaje = f"{event.user.nickname} ha dicho {comentario}"
    if(await mensaje_spam_validacion(comentario)):
        mensaje = f"{event.user.nickname} ha intentando mandar un mensaje SPAM"
    await audio_queue.put(mensaje)

@cliente.on(FollowEvent)
async def aviso_seguidor(event: FollowEvent):
    global alerta_follow
    mensaje = f"@{event.user.nickname} nos ha empezado a seguir"
    print(Fore.LIGHTCYAN_EX + f"[Follow] @{event.user.nickname} nos ha empezado a seguir" + Style.RESET_ALL)
    alerta_follow = True
    await audio_queue.put(mensaje)

@cliente.on(GiftEvent)
async def aviso_donacion(event: GiftEvent):
    global alerta_donacion
    nombre_usuario = event.user.nickname if event.user.nickname else event.user.unique_id
    nombre_regalo = event.gift.name if event.gift.name else "un regalo"
    mensaje = ""

    if(event.gift.streakable and not event.streaking):
        cantidad = event.repeat_count if event.repeat_count else 1
        print(Fore.LIGHTMAGENTA_EX + f"[$] {nombre_usuario} ha donado {cantidad} {nombre_regalo}")
        mensaje = f"{nombre_usuario} ha donado {cantidad} {nombre_regalo}"
    elif(not event.gift.streakable):
        print(Fore.LIGHTMAGENTA_EX + f"[$] {nombre_usuario} ha donado {nombre_regalo}")
        mensaje = f"{nombre_usuario} ha donado un {nombre_regalo}"
    
    alerta_donacion = True
    await audio_queue.put(mensaje)

# prefijos del bot
bot = commands.Bot(command_prefix="$",intents=intents)

# con esta etiqueta le avisamos que la funcion de abajo se maneja como un evento
@bot.event
async def on_ready():
    print(Fore.LIGHTGREEN_EX + f"Bot INICIADO CORRECTAMENTE: {bot.user}, ID: {bot.user.id}" + Style.RESET_ALL)
    bot.loop.create_task(reproducir_comentarios()) # iniciamos el bucle de los comentarios

#con esta etiqueta ya sabe que la funcion es un comando
@bot.command()
async def join(ctx):
    if(ctx.author.voice): # Para verificar que el usuario este conectado a un canal de voz
        global voice_client
        canal = ctx.author.voice.channel #Para saber que canal es
        voice_client = await canal.connect() # guardamos donde esta conectado el bot de discord y lo conectamos
        await ctx.send(f"**[✅] Me conecte a {canal.name}**")
    else:
        await ctx.send("**[❗] ERROR: debes estar conectado a un canal para poder usar este comando**")

@bot.command()
async def leave(ctx):
    if(ctx.voice_client): # Verificamos que el bot este conectado a un canal
        await ctx.voice_client.disconnect() # lo desconectamos del canal
        await ctx.send("**[😪] Ya sali del canal de voz**")
    else:
        await ctx.send("**[❗] No estoy en ningun canal de voz**")

async def main():
    await asyncio.gather(
        bot.start(TOKEN_BOT),  # Inicia el bot de Discord
        cliente.start()        # Inicia el cliente de TikTok Live
    )

# Correr ambos bot
asyncio.run(main())