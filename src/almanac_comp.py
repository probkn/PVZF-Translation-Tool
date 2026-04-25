import json

def find_missing_entries(translation_list, dump_list, key):
    translated_keys = {item[key] for item in translation_list if key in item}
    return [item for item in dump_list if item.get(key) not in translated_keys]

def simple_translate(text):
    if not isinstance(text, str): return text
    rules = { # You can custom here!
        '韧性：': 'HP: ', 
        '移速：': 'Speed: ', 
        '特点：': 'Feature: ',
        '）': ')', 
        '（': '(', 
        '，': ", ", 
        '。': ". ", 
        '：': ": "
    }
    for cn, idn in rules.items():
        text = text.replace(cn, idn)
    
    # Trik khusus Lambat
    if '：慢' in text:
        text = text.replace('：慢', '：Slow')
    return text

def translate_batch(data_list):
    return [{k: simple_translate(v) for k, v in item.items()} for item in data_list]