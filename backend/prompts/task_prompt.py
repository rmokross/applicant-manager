def create_task_propmt(task: str) -> str:
    start = "Werte den Schwierigkeitsgrad der folgenden Aufgabe ein. Gib mir das Ergebnis in JSON Format zurück\
        "
    shape = "\
        {\"Schwierigkeitsgrad\": [Wert zwischen 0-5 mit 0 sehr leicht und 5 sehr schwer]\
        \"Verbesserungspotential\": [Verbesserter Text der Aufgabe. Rechtschreibung, Leseverständnis korrigieren.]"
    prompt = start + task + shape
    return prompt