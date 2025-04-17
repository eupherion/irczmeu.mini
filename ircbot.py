#!/usr/bin/env python3

'''
TOODO:

'''

import socket
import sys, os
import time
import toml
import random
import ast
from math import * # type: ignore
from datetime import datetime

class Config:
    def __init__(self, config_dict):
        self.host = config_dict.get("ircServer", {}).get("ircServerHost")
        self.port = config_dict.get("ircServer", {}).get("ircServerPort")
        self.pswd = config_dict.get("ircServer", {}).get("ircServerPass")

        self.user = config_dict.get("ircClient", {}).get("ircBotUser")
        self.nick = config_dict.get("ircClient", {}).get("ircBotNick")
        self.rnam = config_dict.get("ircClient", {}).get("ircBotRnam")
        self.nspw = config_dict.get("ircClient", {}).get("ircBotNspw")
        self.chan = config_dict.get("ircClient", {}).get("ircBotChan")
        self.admi = config_dict.get("ircClient", {}).get("ircBotAdmi")
        self.acon = config_dict.get("ircClient", {}).get("ircBotAcon")
        self.csym = config_dict.get("ircClient", {}).get("ircBotCsym")
        self.rcon = config_dict.get("ircClient", {}).get("ircBotRcon")
        self.dccv = config_dict.get("ircClient", {}).get("ircBotDccv")

    def print_config(self):
        """
        Выводит значения всех атрибутов объекта класса.
        """
        print("=== IRC Server Configuration ===")
        print(f"Host: {self.host}")
        print(f"Port: {self.port}")
        print(f"Password: {self.pswd}")

        print("\n=== IRC Client Configuration ===")
        print(f"User: {self.user}")
        print(f"Nickname: {self.nick}")
        print(f"Real Name: {self.rnam}")
        print(f"Nickserv Password: {self.nspw}")
        print(f"Channel: {self.chan}")
        print(f"Admin: {self.admi}")
        print(f"Auto Connect: {self.acon}")
        print(f"Command Symbol: {self.csym}")
        print(f"Reconnect: {self.rcon}")
        print(f"DCC Version: {self.dccv}")


def tbytes(s):
	return s.encode("utf-8")

def handle_ctcp_version(source):
	# Отправляем ответ на CTCP VERSION
	version_reply = "\001VERSION IRC bot v1.0.0 (Python)\001"
	irc.send(f"PRIVMSG {source} :{version_reply}\n".encode())
	print('Sent VERSION reply to ' + source + '\r\n')

# Пример функции для обработки входящих сообщений
def process_message(message):
	if message.startswith("PING"):
		# Обработка PING-сообщения
		response = message.replace("PING", "PONG")
		irc.send(response.encode() + b"\r\n")
		print('Sent ' + response + '\r\n')
	elif ("\001VERSION\001") in message:
		# Извлекаем источник сообщения
		source = message.split('!')[0][1:]  # Например, ":nick!user@host" -> "nick"
		handle_ctcp_version(source)
		irc.send(tbytes("JOIN "+ bot.chan +"\r\n"))

def get_datetime():
	now = datetime.now()
	dtnow = now.strftime("%Y-%m-%d %H:%M:%S")
	return dtnow

def parsemsg(s):
	prefix = ''
	trailing = []

	if s[0] == ':':
		prefix, s = s[1:].split(' ', 1)
	if s.find(' :') != -1:
		s, trailing = s.split(' :', 1)
		args = s.split()
		args.append(trailing)
	else:
		args = s.split()
	command = args.pop(0)
	return prefix, command, args

greetings = [
	"hi", "hi!", "hello", "hello!", "olá", "olá!", 
	"ola", "ola!", "bonjour", "salut", "bonjour!", 
	"salut!", "こんにちは!", "你好!", "안녕하세요!", 
	"नमस्ते!", "Hej!", "Hei!, Moi!", "Ciao!"
]

greet_rnd = [
	"it's nice to see you!", ":)", ":D", "^_^"
]

cmd_help = [
	"Each bot command should start with dot \".\":",
	".help, .comm, .calc, .joke, .date, .quit"
]

cmd_list = [
	"Each bot command must start with \".\":",
	" help : Shows general help for beginners.",
	" comm : Shows this message.",
	" calc : Calculator. Usage: !calc 1+1 or !calc sqrt(25).",
	" joke : Tells a joke.",
	" date : Shows current date",
	" time : Shows current time"
]

msg_start = [
	"Hello everyone!",
	"Hello!",
	"Hi!",
	"Olá!",
	"Привет!",
	"Привіт!",
	"Здрасти!",
	"Salut!",
	"Bonjour à tous!",
	"Bună tuturor!"
]

msg_jokes = [
	"A foo walks into a bar, takes a look around and says \"Hello World!\"",
	"Hide and seek champion ; ... since 1958",
	"Why did the programmer quit his job? Because he didn't get arrays. (a raise)",
	"\"Knock-Knock!\" \"Who's there?\" [long pause...] \"Java!\"",
	"Hardware is what you can KICK, Software is what you can yell at.",
	"No Keyboard Detected. Press Any Key to Continue.",
	"Kerbard!",
	"To understand what recursion is, you must first understand recursion.",
	"Seven has the word 'even' in it, which is odd.",
	"How many programmers does it take to change a light bulb? None, it's a hardware problem.",
	"There’s no place like 127.0.0.1",
	"Unix is user-friendly. It's just picky about who its friends are.",
	"$ cat \"food in cans\" -> cat: can't open food in cans",
	"There are only 10 kinds of people in this world: those who know binary and those who don’t.",
	"Have you heard about the new Cray super computer? It’s so fast, it executes an infinite loop in 6 seconds.",
	"I don't see women as objects I see them in a class of her own."
]

msg_asks = {
	"how are you": ["I'm fine, thanks!", "All gears working!", "Not in the mood for bad mood!"],
	"who are you": ["I'm the python Bot!", "I'm the python Bot!"],
	"what can you do": ["I can do a lot of things. Inform new users, tell msg_jokes, calculate big numbers, just type !cmdhelp"]
}

ans = 0
res_calc = 0
msg_helo = True


with open("config.toml", "r") as file:
    config_data = toml.load(file)

bot = Config(config_data)
bot.print_config()

irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

irc.connect((bot.host, bot.port))
irc.send(tbytes("NICK " + bot.nick +"\r\n"))
irc.send(tbytes("USER " + bot.user + " 0 * :Python Bot\r\n"))
irc.send(tbytes("PRIVMSG NickServ :IDENTIFY " + bot.nspw + "\r\n"))
irc.send(tbytes("JOIN "+ bot.chan +"\r\n"))

running = True
while running:
	text = irc.recv(2048).decode("utf-8")
	print(text.strip(" \n\r"))
	process_message(text)
	
	msg = parsemsg(text)

	irc_cmd = msg[1].lower().strip(" ")
	sender = msg[0][:msg[0].rfind("!")].strip(" \n\r")
	
	if msg_helo:
		irc.send(tbytes("PRIVMSG " + bot.chan + " :" + random.choice(msg_start) + "\r\n"))
		msg_helo = False

	if irc_cmd == "privmsg":
		cmd = msg[2][1].lower().strip(" \n\r")
		
		fromchannel = msg[2][0].startswith("#")
		to_cu = bot.chan if fromchannel else sender
		
		for greeting in greetings:
			grets = [
				greeting + " " + bot.nick.lower(),
				greeting + ", " + bot.nick.lower(),
				greeting + "," + bot.nick.lower(),
				bot.nick.lower() + " " + greeting,
				bot.nick.lower() + ", " + greeting,
				bot.nick.lower() + "," + greeting
			]
			if cmd in grets:
				irc.send(tbytes("PRIVMSG " + bot.chan + " :Hello, " + sender + " " + random.choice(greet_rnd) + "\r\n"))
				break
		for question in list(msg_asks.keys()):
			qst = [
				question + " " + bot.nick.lower() + "?",
				question + ", " + bot.nick.lower() + "?",
				question + "," + bot.nick.lower() + "?",
				bot.nick.lower() + " " + question + "?",
				bot.nick.lower() + ", " + question + "?",
				bot.nick.lower() + "," + question + "?",
			]
			if cmd in qst:
				random_answer = random.choice(msg_asks[question])
				irc.send(tbytes("PRIVMSG " + bot.chan + " :" + sender + ", " + random_answer + "\r\n"))
				break

		if (cmd == ".help" or cmd == "!help"):
			for help_line in cmd_help:
				irc.send(tbytes("PRIVMSG " + to_cu + " :" + sender + ": " + help_line + "\r\n"))
		elif cmd == ".comm":
			for help_line in cmd_list:
				irc.send(tbytes("PRIVMSG " + to_cu + " :" + help_line + "\r\n"))
		elif cmd.startswith(".calc"):
			# !calc 1+1
			expr = cmd[5:].strip(" ")
			exec("ans = " + expr)
			irc.send(tbytes("PRIVMSG " + to_cu + " :" + sender + ", " + expr + " = " + str(ans) + "\r\n"))
		
		elif cmd == ".joke":
			random_joke = random.choice(msg_jokes)
			irc.send(tbytes("PRIVMSG " + to_cu + " :" + random_joke + "\r\n"))
		
		elif cmd == ".date":
			date_curr = get_datetime()
			irc.send(tbytes("PRIVMSG " + to_cu + " :" + date_curr + "\r\n"))
		
		elif cmd == ".quit":
			if sender == bot.admi:
				irc.send(tbytes("PRIVMSG " + bot.chan + " :Ok!\r\n"))
				irc.send(tbytes("QUIT :Bye!\r\n"))
				running = False
			else:
				irc.send(tbytes("PRIVMSG " + bot.chan + " :"+sender+", you are not my creator!\r\n"))
	
	time.sleep(1.0 / 30)