import os
import re
import numpy as np
import matplotlib.pyplot as plt


def read_dictionary_file():
    try:
        with open('./ispell.cs/cs_affix.dat', 'r', encoding='utf-8') as file:
            lines = file.readlines()
    except FileNotFoundError:
        print(f'File not found: {file.name}')
        return None

    data_lines = lines[2:]
    affix_rules = []
    current_block = None

    for line in data_lines:
        line = line.split()

        if not line:
            if not current_block:
                continue
            affix_rules.append(current_block)
            current_block = None
            continue

        if not current_block:
            current_block = {
                'type': line[0],
                'identifier': line[1],
                'combinable': line[2],
                'count': line[3],
                'rules': []
            }
            continue

        current_rule = {
            'type': line[0],
            'identifier': line[1],
            'symbols_to_cut': line[2],
            'sequence_to_add': line[3],
            'REGex_condition': line[4],
        }
        current_block['rules'].append(current_rule)

    return affix_rules

def categorize_string(string: str) -> str:
    pattern = re.compile(r'\{.*\}')
    if '/' in string and pattern.match(string):
        return 'both'
    elif '/' in string:
        return 'slash'
    elif pattern.match(string):
        return 'curly'
    else:
        return 'none'

def apply_affix_rules_to_file(affix_rules, apply_to_filepath):
    words_to_process = []
    try:
        with open(apply_to_filepath, 'r', encoding='utf-8') as file:
            for words in file.readlines():
                words = words.strip()
                if not words:
                    continue
                if ' ' in words:
                    for word in words.split(' '):
                        words_to_process.append(word)
                else:
                    words_to_process.append(words)


    except FileNotFoundError:
        print(f'File not found: {apply_to_filepath}')

    output_file = []
    for word in words_to_process:
        match categorize_string(word):
            case 'none':
                output_file.append(word)
            case 'slash':
                res = apply_affix_rules_to_word(affix_rules, word)
                for y in res:
                    output_file.append(y)
            case 'curly':
                for variation in create_word_variations(word):
                    output_file.append(variation)
            case 'both':
                variations = create_word_variations(word)
                for variation in variations:
                    res = apply_affix_rules_to_word(affix_rules, variation)
                    for y in res:
                        output_file.append(y)

    return output_file

def create_word_variations(word: str):

    pattern = re.compile(r'\{(.+?)\}(.+)')  ###
    match = pattern.match(word)  ###

    word_variations = []
    for part in match.group(1).split(','):
        new_word = part + f'{match.group(2)}'
        word_variations.append(new_word)

    return word_variations

def apply_affix_rules_to_word(affix_rules, word: str):
    parts = word.split('/')
    word = parts[0]
    rules_to_use = list(parts[1])

    variations = set()
    variations.add(word)

    #print(word)

    for rule_to_use in rules_to_use:
        for rule_block in affix_rules:
            if rule_block['identifier'] == rule_to_use:
                for rule in rule_block['rules']:
                    if rule['type'] == 'PFX':
                        new_word = rule['sequence_to_add'] + word
                        variations.add(new_word)
                    if rule['type'] == 'SFX':
                        regex = f"r\'{rule['REGex_condition']}\'"
                        regex_pattern = re.compile(regex)
                        if regex_pattern.match(word):
                            #print(rule)
                            if rule['symbols_to_cut'] == '0':
                                new_word = word + rule['sequence_to_add']
                                variations.add(new_word)
                            else:
                                if word.endswith(rule['symbols_to_cut']):
                                    new_word = word[:-len(rule['symbols_to_cut'])] + rule['sequence_to_add']
                                    variations.add(new_word)
    return variations

def count_words_for_filename(file_name):
    cat_path = f'./ispell.cs/cat/{file_name}'
    out_path = f'./ispell.cs/out/{file_name}'
    file_name = file_name[:-4]
    return [f'{file_name}', count_words(cat_path), count_words(out_path)]

def count_words(filepath):
    summ = 0
    with open(filepath, 'r', encoding='utf-8') as file:
        for words in file.readlines():
            words = words.strip()
            if not words:
                continue
            if ' ' in words:
                summ += len(words.split(' '))
            else:
                summ += 1
    return summ

def create_graph(data):
    names = [item[0] for item in data]
    start_count = [item[1] for item in data]
    out_count = [item[2] for item in data]

    x = np.arange(len(names))
    width = 0.35

    fig, ax = plt.subplots(figsize=(15, 8))
    rects1 = ax.bar(x - width / 2, start_count, width, label='Start', color='blue')
    rects2 = ax.bar(x + width / 2, out_count, width, label='End', color='magenta')
    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=45, ha='right')
    ax.legend()
    fig.tight_layout()
    plt.show()

def get_word_length_stats(data):
    lengths = [len(word) for word in data]
    shortest_length = min(lengths)
    longest_word = max(lengths)
    average_word_length = sum(lengths) / len(lengths)
    return {
        'short': shortest_length,
        'long': longest_word,
        'avg': average_word_length
    }

def create_word_size_graph(data):
    categories = [item[0] for item in data]
    short_sizes = [item[1]['short'] for item in data]
    long_sizes = [item[1]['long'] for item in data]
    avg_sizes = [item[1]['avg'] for item in data]

    x = np.arange(len(categories))
    width = 0.25

    fig, ax = plt.subplots(figsize=(15, 6))
    rects1 = ax.bar(x - width, short_sizes, width, label='Short', color='skyblue')
    rects2 = ax.bar(x, long_sizes, width, label='Long', color='coral')
    rects3 = ax.bar(x + width, avg_sizes, width, label='Avg', color='lightgreen')

    ax.set_ylabel('Sizes')
    ax.set_xlabel('Categories')
    ax.set_title('Category Sizes')
    ax.set_xticks(x)
    ax.set_xticklabels(categories, rotation=45, ha="right")
    ax.legend()

    fig.tight_layout()
    plt.show()


if __name__ == '__main__':
    dictionary_data = read_dictionary_file()
    files_to_work_with = os.listdir('./ispell.cs/cat')
    if not os.path.exists('./ispell.cs/out'):
        os.mkdir('./ispell.cs/out')
    files_to_work_with_loaded = []

    for filename in files_to_work_with:
        if filename.endswith('.cat'):
            print(f'Working with file: {filename}')
            path = f'./ispell.cs/cat/{filename}'
            out = apply_affix_rules_to_file(dictionary_data, path)
            save_path = f'./ispell.cs/out/{filename}'
            print(f'Saving file: {filename}')
            with open(save_path, 'w', encoding='utf-8') as new_file:
                for x in out:
                    new_file.write(x)
                    new_file.write('\n')

    statistics = []

    for filename in files_to_work_with:
        statistics.append(count_words_for_filename(filename))

    create_graph(statistics)

    word_length_stats = []

    for filename in files_to_work_with:
        file = open(f'./ispell.cs/out/{filename}', 'r', encoding='utf-8')
        word_length_stats.append((filename[:-4], get_word_length_stats(file)))
        file.close()

    create_word_size_graph(word_length_stats)
