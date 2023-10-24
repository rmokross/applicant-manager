import openai
import json

with open('../.secrets', 'r') as f:
    openai.api_key = f.read()

def create_message(prompt: str) -> list:
    messages = [{"role": "system",
                 "content": prompt}]
    return messages

def exec_prompt(prompt: str) -> str:
    messages = create_message(prompt)
    try:
        chat = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=messages
        ) 
        reply = chat.choices[0].message.content 
        return reply
    except Exception as e:
        print(e)
        return None

def get_data_from_reply(reply: str) -> json:
    try:
        json_start_index = reply.find("{")
        json_stop_index = reply.find("}") + 1

        data = json.loads(reply[json_start_index:json_stop_index])
        return data
    except Exception as e:
        print(str(e))
        return None


if __name__=="__main__":

    prompt1 = "Werte den Schwierigkeitsgrad der folgenden Aufgabe ein. Gib mir das Ergebnis in JSON Format zurück\
        Schreibe eine Query, mit welche alle Autos mit einem Baujahr zwischen 1965 und 1977 zurückgegeben werden. Frage die Daten von der Tabelle 'cars' ab.\
        \
        {\"Schwierigkeitsgrad\": [Wert zwischen 0-5 mit 0 sehr leicht und 5 sehr schwer]\
        \"Verbesserungspotential\": [Verbesserter Text der Aufgabe. Rechtschreibung, Leseverständnis korrigieren.]"

    reply = exec_prompt(prompt1)
    print(reply)
    print(get_data_from_reply(reply))