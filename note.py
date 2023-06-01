from collections import UserDict
import json
from json import JSONDecodeError


class NoteNameNotProvided(Exception):
    pass


class NoteDoesNotExist(Exception):
    pass


class SearchValueNotProvided(Exception):
    pass


class FieldNote:
    def __init__(self, value):

        if not isinstance(value, str):
            raise ValueError('Value must be a string')
        self.value = value

    def __str__(self) -> str:
        return str(self.value)
    
    def __repr__(self) -> str:
        return str(self)
    
    def to_json(self):
        return self.__str__()


class Note(FieldNote):

    def __init__(self, name, text, tags=None):
        self.name = name
        self.text = text
        self.tags = [*tags.value] if tags else []

    def add_tag(self, tag):
        if isinstance(tag, list):
            self.tags.extend(tag)
        elif len(tag) == 0:
            self.tags = []
        else:
            self.tags.append(tag)


class NameNote(FieldNote):
    def __init__(self, value):
        self.__value = None
        self.value = value

    @property
    def value(self):
        return self.__value
    
    @value.setter
    def value(self, value):
        if not isinstance(value, str):
            raise ValueError('Must be a string')
        if len(value) < 1:
            raise ValueError('Name must be more than 0 characters')
        if len(value) > 15:
            raise ValueError('Name must be less than 15 characters')
        self.__value = value


class Text(FieldNote):
    def __init__(self, value):
        self.value = value


class Tag(FieldNote):
    def __init__(self, value):
        self.value = value


class NoteEncoder(json.JSONEncoder):
    def default(self, obj):

        if isinstance(obj, Note):
            return obj.__dict__
    
        return obj.to_json()


class NoteBook(UserDict):

    def add_notes(self, note:Note):
        self.data[note.name.value] = note

    def paginator(self, iter_obj, page=1):
        start = 0

        while True:
            
            result_keys = list(iter_obj)[start:start + page]
            result = ' '.join([f'{k}: {iter_obj.get(k).text.value}' for k in result_keys])
            if not result:
                break
            yield result
            start += page

    def recover_from_file(self):
        try:
            with open('notes_book.json') as fd:
                data = json.load(fd)
        except (FileNotFoundError, AttributeError, JSONDecodeError, ValueError):
            return {}

        for k, v in data.items():
            if v['tags']:
                self.add_notes(Note(NameNote(v['name']), Text(v['text']), Tag(v['tags'])))
            else:
                self.add_notes(Note(NameNote(v['name']), Text(v['text'])))

    def save_to_file(self):

        with open('notes_book.json', "w") as fd:
            if self.data:
                json.dump(self.data, fd, cls=NoteEncoder, indent=3)


def input_error(func):
    def inner(*args):
        try:
            return func(*args)
        except ValueError:
            print('Not enough params. Type help.')
        except NoteNameNotProvided:
            print("You haven't note name provided!")
        except NoteDoesNotExist:
            print("Note with this name doesn't exist!")
        except SearchValueNotProvided:
            print("You haven't provided what to search!")
    return inner


def list_of_params(*args):

    container = args[0]

    if len(container) < 2:
        raise ValueError

    return container


@input_error
def add_note(note_book, *args):

    lst = list_of_params(*args)

    if len(lst) > 1:
        note_name = lst[0]
        note_text = lst[1:]
        note_book.add_notes(Note(NameNote(note_name), Text(' '.join(note_text))))

        if lst[0] in [k for k in note_book.keys()]:

            note_tags = input('Please enter tags for this note: ').strip().split()
            note_book.get(lst[0]).add_tag(note_tags)

        return f'Note with name: {note_name} was added'
    else:
        raise ValueError


def show_notes(note_book, *args):
    gen_obj = note_book.paginator(note_book)

    for i in gen_obj:
        print('*' * 50)
        print(i)
        input('Press any key to see next note.')

    return "You don't have more notes."


@input_error
def add_tag(note_book, *args):
    lst = list_of_params(*args)

    if len(lst) > 1:
        note_book.get(lst[0]).add_tag(lst[1:])
        return f'Note {lst[0]} was update'
    else:
        raise ValueError


@input_error
def get_notes(note_book, *args):

    lst = args[0]
    if len(lst) < 1:
        raise SearchValueNotProvided

    search_value = lst[0]

    list_of_notes = {}

    for k, v in note_book.items():
        if lst[0] == k:
            return f'{search_value}: {v.text}'

        if str(v.text).startswith(search_value):
            list_of_notes.update({k: v.text})

        if k.startswith(lst[0]):
            list_of_notes.update({k: v.text})

    if list_of_notes:
        return list_of_notes
    return f'Not notes that start with {search_value}'


@input_error
def remove_note(note_book, *args):

    lst = args[0]
    if len(lst) < 1:
        raise NoteNameNotProvided

    name = lst[0]
    note_exists = note_book.get(name)

    if not note_exists:
        raise NoteDoesNotExist

    note_book.pop(name)

    return f'Note with name {name} was deleted'


choices = {
            'add note': add_note,
            'show notes': show_notes,
            'add tag': add_tag,
            'remove note': remove_note,
            'note': get_notes
           }
