import requests
import time
from datetime import datetime
import configparser

class DiscordKarutaDropBot:
    def __init__(self, channel_id, token, cooldown_duration=30 * 60):
        self.url_get = f"https://discord.com/api/v9/channels/{channel_id}/messages"
        self.url_post = f"https://discord.com/api/v9/channels/{channel_id}/messages"
        self.auth = {
            'Authorization': token
        }
        self.cooldown_duration = cooldown_duration
        self.last_response_time = 0

    def get_messages_since(self, last_message_id):
        params = {
            'after': last_message_id
        }
        response = requests.get(self.url_get, headers=self.auth, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def send_message(self, content):
        msg = {
            'content': content
        }
        requests.post(self.url_post, headers=self.auth, data=msg)

    def format_cooldown_time(self, seconds):
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes} minutes et {seconds} secondes"

    def listen_for_new_messages(self):
        last_message_id = None
        while True:
            try:
                messages = self.get_messages_since(last_message_id)
                if messages:
                    for message in messages:
                        if "drop me" in message['content'].lower():
                            current_time = time.time()
                            current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            if self.last_response_time == 0 or current_time - self.last_response_time >= self.cooldown_duration:
                                self.send_message("Voici un drop :smile: !")
                                self.send_message("kd")
                                print(f"[INFO : {current_datetime}] : Drop en cours")
                                self.last_response_time = current_time
                            else:
                                cooldown_remaining = self.cooldown_duration - int(current_time - self.last_response_time)
                                cooldown_time_str = self.format_cooldown_time(cooldown_remaining)
                                self.send_message(f"Mince j'ai un cooldown :cry: , Temps restant : **`{cooldown_time_str}`**")
                                print(f"[INFO : {current_datetime}] : Cooldown")
                            last_message_id = message['id']
                            break
            except requests.exceptions.HTTPError as http_err:
                if http_err.response.status_code == 429:
                    retry_after = float(http_err.response.headers.get('Retry-After', '2'))
                    time.sleep(retry_after)
                else:
                    print("HTTP error occurred:", http_err)
            except Exception as e:
                print("Erreur lors de la récupération des messages :", e)


if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read("configBot.ini")

    channel_id = int(config.get("DiscordKarutaBot", "channel_id"))
    token = config.get("DiscordKarutaBot", "token")
    cooldown_duration = int(config.get("DiscordKarutaBot", "cooldown_duration_min")) * 60

    bot = DiscordKarutaDropBot(channel_id, token, cooldown_duration)
    bot.listen_for_new_messages()
