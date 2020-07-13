from string import ascii_letters

def list_letters():
    print(ascii_letters)

CHARLIMIT_NAME = 28

long_names = [
    'Jose Inarritu Gonzallez Ima La Piena Hugo',
    'FirstName LastName',
    'Ewe One TwoMakingLong Three LastName',
    'Nebeprisikiskiakopusteliaudamasis LastName',
    'Clémence Clémence (Chez Jeannie MENSCH)'
    ]


def shorten_middle_name(long_name : str) -> str:
    '''replaces middle names with abbreviations. Example:
    input: Jose Inarritu Gonzallez Ima La Piena Hugo
    output: Jose I. G. I. L. P. Hugo'''
    shortened_name_lst = []
    try:
        words_inside = long_name.split()
        print(words_inside)
        for idx, word in enumerate(words_inside):
            if idx == 0 or idx == len(words_inside) - 1:
                shortened_name_lst.append(word)
            else:
                print(f'About to abbreviate word: {word}')
                abbr_word = abbreviate_word(word)
                shortened_name_lst.append(abbr_word)
        short_name = ' '.join(shortened_name_lst)
        print(f'Short version: {short_name}, len: {len(short_name)}')
        assert len(short_name) <= CHARLIMIT_NAME, 'Short name did not pass charlimit validation'
        return short_name        
    except Exception as e:
        print(f'Could not shorten name. Error: {e}')
        print('VBA_ERROR')
        return long_name

def abbreviate_word(word : str) -> str:
    '''returns capitalized first letter with dot of provided word'''
    if all(char in ascii_letters for char in word):
        print(f'Word {word} is ascii letters only')
    else:
        print(f'Word {word} has another characters!')

    return  word[0].upper() + '.' if word[0] in ascii_letters else word

def run():
    for idx, name in enumerate(long_names):
        if len(name) > CHARLIMIT_NAME:
            short_name = shorten_middle_name(name)
            print(f'{idx}: {short_name}')
        else:
            print(f'{idx}: {name}')

if __name__ == "__main__":
    run()
    # list_letters()