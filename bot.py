import speech_recognition as sr
import openai
import requests
import wikipediaapi
import pywhatkit
import webbrowser
import sys
import PySimpleGUI as sg
import os
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from googletrans import Translator
from gtts import gTTS
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import playsound
from datetime import datetime, timedelta
import time

# Configurações
openai.api_key = 'sk-proj-MozJFvz94KKbgUVCSMKST3BlbkFJxzmkbj9wTqJ4uknSZCfd'
weather_api_key = 'bf3fd5205794430d12d8e8e2df848c15'
news_api_key = '68e70c1f8fee41da890b52c425e19ca4'
smtp_server = 'smtp.gmail.com'
smtp_port = 587 
smtp_username = ' Your gmail'
smtp_password = ' Your password'

# Inicialização do Wikipedia
wiki_wiki = wikipediaapi.Wikipedia('pt')

# Configuração do WebDriver para o Chrome
chrome_options = Options()
chrome_options.add_argument("--headless")  # Executa o navegador em modo headless (sem interface gráfica)
chrome_service = Service('caminho/para/chromedriver')  # Substitua pelo caminho para seu chromedriver

# Função para converter texto em áudio e reproduzi-lo
def speak(text):
    tts = gTTS(text=text, lang='pt')
    filename = 'temp_audio.mp3'
    tts.save(filename)
    playsound.playsound(filename)
    os.remove(filename)

# Função para reconhecer fala
def recognize_speech_from_mic():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        speak("Diga algo...")
        audio = recognizer.listen(source)

    try:
        response = recognizer.recognize_google(audio, language='pt-BR')
        speak("Você disse: " + response)
        return response
    except sr.UnknownValueError:
        speak("Desculpe, não entendi o que você disse.")
        return None
    except sr.RequestError:
        speak("Erro ao tentar acessar o serviço de reconhecimento de voz.")
        return None

# Função para processar comandos com NLP
def process_command(command):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=command,
        max_tokens=50
    )
    return response.choices[0].text.strip()

# Função para buscar informações na Wikipedia
def search_wikipedia(query):
    page = wiki_wiki.page(query)
    if page.exists():
        speak("Título: " + page.title)
        speak("Resumo: " + page.summary[:500])
    else:
        speak("Página não encontrada.")

# Função para enviar mensagem no WhatsApp
def send_whatsapp_message(number, message):
    pywhatkit.sendwhatmsg_instantly(number, message)
    speak(f"Mensagem enviada para {number}")

# Função para obter informações meteorológicas de Curitiba
def get_weather():
    city = 'Curitiba,BR'
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={weather_api_key}&units=metric&lang=pt'
    response = requests.get(url)
    data = response.json()
    
    if response.status_code == 200:
        main = data['main']
        weather = data['weather'][0]
        speak(f"Clima em Curitiba, Paraná:")
        speak(f"Temperatura: {main['temp']}°C")
        speak(f"Condição: {weather['description']}")
    else:
        speak("Erro ao acessar a API de clima")

# Função para listar arquivos em um diretório
def list_files(directory):
    try:
        files = os.listdir(directory)
        if files:
            speak(f"Arquivos no diretório {directory}:")
            for file in files:
                speak(file)
        else:
            speak(f"O diretório {directory} está vazio.")
    except Exception as e:
        speak(f"Erro ao listar arquivos: {e}")

# Função para gerar número aleatório
def generate_random_number(start, end):
    number = random.randint(start, end)
    speak(f"Número aleatório entre {start} e {end}: {number}")

# Função para abrir aplicativos
def open_application(app_name):
    try:
        if app_name.lower() == "youtube music":
            webbrowser.open("https://music.youtube.com/")
            speak("Abrindo YouTube Music")
        else:
            os.system(f'start {app_name}')
            speak(f"Abrindo {app_name}")
    except Exception as e:
        speak(f"Erro ao abrir aplicativo: {e}")

# Função para tocar música no YouTube Music
def play_music_on_youtube_music(music_name):
    search_query = music_name.replace(' ', '+')
    webbrowser.open(f"https://music.youtube.com/search?q={search_query}")
    speak(f"Tocando música: {music_name} no YouTube Music")

# Função para pesquisar em um aplicativo específico
def search_in_application(app_name, query):
    if app_name.lower() == "google chrome":
        webbrowser.get('google-chrome').open(f"https://www.google.com/search?q={query}")
        speak(f"Pesquisando '{query}' no Google Chrome")
    elif app_name.lower() == "firefox":
        webbrowser.get('firefox').open(f"https://www.google.com/search?q={query}")
        speak(f"Pesquisando '{query}' no Firefox")
    elif app_name.lower() == "youtube":
        webbrowser.open(f"https://www.youtube.com/results?search_query={query}")
        speak(f"Pesquisando '{query}' no YouTube")
    else:
        webbrowser.open(f"https://www.google.com/search?q={query}")
        speak(f"Pesquisando '{query}' no navegador padrão")

# Função para controlar a música no YouTube Music
def control_youtube_music(action):
    try:
        driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
        driver.get("https://music.youtube.com/")
        wait = WebDriverWait(driver, 20)

        # Esperar o carregamento da página
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "ytmusic-play-button-renderer")))

        if action.lower() == "pausar":
            play_button = driver.find_element(By.CSS_SELECTOR, "ytmusic-play-button-renderer")
            if "pause" in play_button.get_attribute("aria-label").lower():
                play_button.click()
                speak("Música pausada.")
            else:
                speak("A música já está pausada.")
        elif action.lower() == "despausar":
            play_button = driver.find_element(By.CSS_SELECTOR, "ytmusic-play-button-renderer")
            if "play" in play_button.get_attribute("aria-label").lower():
                play_button.click()
                speak("Música despausada.")
            else:
                speak("A música já está tocando.")
        elif action.lower() == "próximo":
            next_button = driver.find_element(By.CSS_SELECTOR, "ytmusic-next-button-renderer")
            next_button.click()
            speak("Avançando para a próxima faixa.")
        elif action.lower() == "anterior":
            previous_button = driver.find_element(By.CSS_SELECTOR, "ytmusic-previous-button-renderer")
            previous_button.click()
            speak("Voltando para a faixa anterior.")
        else:
            speak("Ação desconhecida para controle de música.")
        
        driver.quit()  # Fechar o WebDriver após o uso
    except Exception as e:
        speak(f"Erro ao controlar a música: {e}")

# Função para ler as principais notícias usando NewsAPI
def read_news():
    url = f'https://newsapi.org/v2/top-headlines?country=br&apiKey={news_api_key}'
    response = requests.get(url)
    data = response.json()
    
    if response.status_code == 200:
        articles = data['articles']
        speak("Principais notícias:")
        for article in articles[:5]:  # Limitar a 5 notícias
            speak(f"Título: {article['title']}")
            speak(f"Descrição: {article['description']}")
            speak(f"URL: {article['url']}")
            speak()
    else:
        speak("Erro ao acessar a API de notícias")

# Função para agendar lembrete
def set_reminder(reminder_time, message):
    try:
        reminder_time = datetime.strptime(reminder_time, "%H:%M")
        now = datetime.now()
        reminder_datetime = now.replace(hour=reminder_time.hour, minute=reminder_time.minute, second=0, microsecond=0)
        
        if reminder_datetime < now:
            reminder_datetime += timedelta(days=1)  # Agendar para o próximo dia se o horário já passou

        time_to_wait = (reminder_datetime - now).total_seconds()
        speak(f"Lembrete agendado para {reminder_datetime.strftime('%H:%M')}.")
        time.sleep(time_to_wait)
        speak(f"Lembrete: {message}")
    except Exception as e:
        speak(f"Erro ao agendar lembrete: {e}")

# Função para enviar e-mail
def send_email(subject, body, to_email):
    try:
        msg = MIMEMultipart()
        msg['From'] = smtp_username
        msg['To'] = to_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain'))
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.sendmail(smtp_username, to_email, msg.as_string())
        speak(f"E-mail enviado para {to_email}")
    except Exception as e:
        speak(f"Erro ao enviar e-mail: {e}")

# Função principal para lidar com os comandos
def handle_command(command):
    if "Wikipedia" in command:
        query = command.split("Wikipedia sobre")[-1].strip()
        search_wikipedia(query)
    elif "mensagem" in command:
        parts = command.split("mensagem para")
        number_message = parts[-1].strip().split("dizendo")
        number = number_message[0].strip()
        message = number_message[-1].strip()
        send_whatsapp_message(number, message)
    elif "abrir" in command:
        app_name = command.split("abrir")[-1].strip()
        open_application(app_name)
    elif "tocar música" in command:
        music_name = command.split("tocar música")[-1].strip()
        play_music_on_youtube_music(music_name)
    elif "clima em Curitiba" in command:
        get_weather()
    elif "listar arquivos" in command:
        directory = command.split("listar arquivos em")[-1].strip()
        list_files(directory)
    elif "gerar número aleatório" in command:
        range_values = command.split("entre")[-1].strip().split("e")
        start = int(range_values[0].strip())
        end = int(range_values[1].strip())
        generate_random_number(start, end)
    elif "pesquisar no" in command:
        parts = command.split("pesquisar no")
        app_name = parts[1].split("sobre")[0].strip()
        query = parts[1].split("sobre")[-1].strip()
        search_in_application(app_name, query)
    elif "controlar música" in command:
        action = command.split("controlar música")[-1].strip()
        control_youtube_music(action)
    elif "notícias" in command:
        read_news()
    elif "lembrete" in command:
        parts = command.split("lembrete para")
        reminder_details = parts[-1].strip().split("dizendo")
        reminder_time = reminder_details[0].strip()
        message = reminder_details[1].strip()
        set_reminder(reminder_time, message)
    elif "enviar e-mail" in command:
        parts = command.split("enviar e-mail para")
        email_details = parts[-1].strip().split("assunto")
        to_email = email_details[0].strip()
        subject_body = email_details[1].strip().split("corpo")
        subject = subject_body[0].strip()
        body = subject_body[1].strip()
        send_email(subject, body, to_email)
    elif "fechar" in command:
        speak("Fechando o programa.")
        sys.exit()
    else:
        response = process_command(command)
        speak("Resposta: " + response)

# Interface gráfica com PySimpleGUI
layout = [
    [sg.Text('Assistente Virtual')],
    [sg.Output(size=(50, 10), key='output')],
    [sg.Button('Iniciar'), sg.Button('Sair')]
]

window = sg.Window('Assistente Virtual', layout)

# Loop principal da GUI
while True:
    event, values = window.read()
    if event == sg.WINDOW_CLOSED or event == 'Sair':
        break
    if event == 'Iniciar':
        command = recognize_speech_from_mic()
        if command:
            handle_command(command)

window.close()
