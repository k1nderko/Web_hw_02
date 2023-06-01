import re
from datetime import datetime, date
from collections import UserDict
import json
from json.decoder import JSONDecodeError


def input_error(func):
    def inner(*args):
        try:
            return func(*args)
        except EmptyNameField:
            print("Field name shouldn't be empty!")
        except ContactAlreadyExists:
            print("Contact with this name already exists!")
        except ContactDoesNotExist:
            print("Contact with this name does not exist!")
        except PhonesDataMissingError:
            print("You haven't provided phones!")
        except EmptySearchQuery:
            print("You haven't provided search query!")
        except EmptyMailField:
            print("You haven't provided mail!")
        except EmptyBirthdayField:
            print("You haven't provided birthday query!")
        except IncorrectDateField:
            print("Incorrent Birthday date!")
        except IncorrectPhoneField:
            print("Incorrent Phone format!")
        except PerpageParameterMissing:
            print("You haven't provided contact number per page!")
    return inner

def date_error(func):
    def inner(*args):
        try:
            return func(*args)
        except ValueError:
            print("You've entered not valid date!")
    return inner

def file_error(func):
    def inner(*args):
        try:
            return func(*args)
        except FileNotFoundError:
            pass
        except JSONDecodeError:
            pass 
    return inner


class EmptyNameField(Exception):
    pass


class ContactAlreadyExists(Exception):
    pass
   

class ContactDoesNotExist(Exception):
    pass


class PhonesDataMissingError(Exception):
    pass


class EmptySearchQuery(Exception):
    pass

class EmptyMailField(Exception):
    pass

class EmptyBirthdayField(Exception):
    pass


class IncorrectDateField(Exception):
    pass


class IncorrectPhoneField(Exception):
    pass


class PerpageParameterMissing(Exception):
    pass


class Field:

    def __init__(self):
        self._value = ''

    def includes_value(self, value):
        if value in self.value:
            return True
        return False
    
    def update(self, value):
        self._value = value


class Name(Field):

    def __init__(self, name):
        self.value = name
    
    def is_the_same_name(self, name):
        return self.value == name


class Phone(Field):

    def __init__(self, phone):
        self._value = ''
        self.value = phone

    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, new_value):
        match = re.match(r'^(\+38)?0\d{2}[-\s]?\d{3}[-\s]?\d{2}[-\s]?\d{2}', new_value)
        if not match:
            raise IncorrectPhoneField
        self._value = new_value


class Mail(Field):

    def __init__(self, mail):
        self.value = mail
        
    def is_the_same_mail(self, mail):
        return self.value == mail


class Birthday(Field):

    def __init__(self, birthday):
        self._value = birthday

    def __str__(self):
        return datetime.strftime(self._value(), "%d.%m.%Y")
    
    @property
    def value(self):
        return self._value
      
    @value.setter
    @date_error
    def value(self, new_value):
        match = re.match(r'\d{2}[\.]\d{2}[\.]\d{4}', new_value)

        if not match:
            raise IncorrectDateField
        
        self._value = datetime.strptime(new_value, "%d.%m.%Y").date()
              

class AddressBook(UserDict):

    def __init__(self):
        super().__init__()
        self.initialize()

    @file_error
    def initialize(self):

        with open("contacts.txt", "r") as fh:

            data = json.load(fh)

            for name, record in data.items():

                name = Name(name)
                rec = Record(name)
                rec.phones = [Phone(phone) for phone in record["phones"]]
                rec.mail = [Mail(mail) for mail in record["mail"]]
                birthday = datetime.strptime(record["birthday"], '%d %B %Y').date() if record["birthday"] else None
                rec.birthday = Birthday(birthday)
                self.add_record(rec)

    def save_data(self):
        with open("contacts.txt", "w") as fh:

            data = {record.name.value: {"phones": [i.value for i in record.phones], 
                                    "mail": record.mail.value if record.mail.value else None,
                                    "birthday": record.birthday.value.strftime('%d %B %Y') if record.birthday.value else None} 
                                    for record in self.data.values()}
            json.dump(data, fh)

    def show_all_contacts(self):
        return self.format_records(self.data.values())   
    
    def add_record(self, record):
        self.data[record.name.value] = record
        
    def find_records(self, query):
        result = [record for record in self.data.values() if record.find_coincidence(query)]
        return self.format_records(result)
        
    def delete_record(self, name): 
        self.data.pop(name)

    def get_record_by_name(self, name):
        return self.data.get(name, None)

    def format_records(self, data):

        if data:
            return '\n'.join([f"Name: {record.name.value} | "
                              f"phones: {', '.join([i.value for i in record.phones]) if record.phones else '-'} | "
                              f"mail: {record.mail.value} | "
                              f"birthday: {record.birthday.value if record.birthday.value else '-'}"
                              for record in data])
        return None
    
    def iterator(self, per_page):
        current_value = 0
        page = 1
        count = []


        while current_value < len(self.data.values()):

            count.append(list(self.data.values())[current_value])

            if len(count) == per_page or current_value == len(self.data.values()) - 1:

                print(f"PAGE {page}: ")
                page += 1
                yield self.format_records(count)
                count = []
            
            current_value += 1


class Record:
    phones = []
    mail = None
    birthday = None

    def __init__(self, name):
        self.name = name

    def has_mail(self):
        if self.mail.value:
            return True
        return False
    
    def has_birthday(self):
        if self.birthday.value:
            return True
        return False

    def compare_name(self, name):
        return self.name.value == name
    
    def find_coincidence(self, value):
        result = (self.name.includes_value(value) or 
                  list(filter(lambda x: x.includes_value(value), self.phones)))
        return result

    def update(self, phones):
        self.phones = phones

    def get_days_to_birthday(self):
        
        if self.birthday.value:
            today = date.today() 
            birthday_this_year = date(year=today.year, month=self.birthday.value.month, day=self.birthday.value.day)
            print("birthday_this_year", birthday_this_year)
            delta = birthday_this_year - today 

            if birthday_this_year > today :
                return delta.days
            
            birthday_next_year = date(year=today.year+1, month=self.birthday.value.month, day=self.birthday.value.day)
            delta = birthday_next_year - today 
            return delta.days
        
        return None


def format_phones_to_list(data):
    return list(map(lambda x: Phone(x.strip()), data)) if data else []


def show_all_contacts(address_book, *args):
    result = address_book.show_all_contacts()
    if result:
        return result
    return "There are no contacts!"

def find_records(address_book, params):

    if not params:
        raise EmptySearchQuery

    query = params[0]
    result = address_book.find_records(query)

    return result if result else "Nothing found!"

@input_error
def add_record(address_book, params):

    if not params:
        raise EmptyNameField

    name = params[0]

    contact = address_book.get_record_by_name(name)
    if contact:
        raise ContactAlreadyExists

    name_obj = Name(name)
    record = Record(name_obj)


    phones = params[1:]
    if phones:
        record.phones = format_phones_to_list(phones)

    mail = Mail(None)
    record.mail = mail
 
    birthday = Birthday(None)
    record.birthday = birthday

    address_book.add_record(record)
    address_book.save_data()
    return f"Contact with name {name} created!"
 
@input_error
def delete_record(address_book, params):
    if not params:
        raise EmptyNameField

    name = params[0]

    contact = address_book.get_record_by_name(name)

    if not contact:
        raise ContactDoesNotExist

    address_book.delete_record(name)
    address_book.save_data()
    return f"Contact with name {name} deleted!"

@input_error
def update(address_book, params):

    if not params:
        raise EmptyNameField

    name = params[0]
    
    record = address_book.get_record_by_name(name)

    if not record:
        raise ContactDoesNotExist
    
    if len(params) == 1:
        raise PhonesDataMissingError
    
    phones = params[1:] 
    # print([Phone(phone) for phone in phones])

    phones = format_phones_to_list(phones)
     
    record.update(phones)
    address_book.save_data()
    return f"Field <phones> for record with name {name} updated!"

@input_error
def update_birthday(address_book, params):

    if not params:
        raise EmptyNameField

    name = params[0]

    contact = address_book.get_record_by_name(name)

    if not contact:
        raise ContactDoesNotExist
    
    if len(params) < 2:
        raise EmptyBirthdayField
    
    birthday = params[1]
    contact.birthday.value = birthday
    address_book.save_data()

    return f"Field <birthday> for record with name {name} updated!"

@input_error
def update_mail(address_book, params):

    if not params:
        raise EmptyNameField

    name = params[0]

    contact = address_book.get_record_by_name(name)

    if not contact:
        raise ContactDoesNotExist
    
    if len(params) < 2:
        raise EmptyMailField
    
    mail = params[1]
    contact.mail.value = mail
    address_book.save_data()

    return f"Field <mail> for record with name {name} updated!"

@input_error
def check_birthday(address_book, params):
    if not params:
        raise EmptyNameField

    name = params[0]

    contact = address_book.get_record_by_name(name)

    if not contact:
        raise ContactDoesNotExist
    
    has_birthday = contact.has_birthday()
    if has_birthday:
        days = contact.get_days_to_birthday()
        return f"There are {days} days left to {name}'s birthday!"
    return f"Field <birthday> for {name} is empty!"


@input_error
def iterator(address_book, params):

    if not params:
        raise PerpageParameterMissing

    per_page = int(params[0])
    iterator = address_book.iterator(per_page)

    for i in iterator:
        print(i)


actions = {
    "show all": show_all_contacts,
    "update birthday": update_birthday,
    "add": add_record,
    "find": find_records,
    "update": update,
    "mail": update_mail,
    "delete": delete_record,
    "check birthday": check_birthday,
    "iterator": iterator
}
