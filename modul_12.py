import cmd
import pickle
from collections import UserDict
from datetime import datetime, timedelta

class Field:
    def __init__(self, value):
        self._value = None 
        self.value = value 

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        self._value = new_value

    def __str__(self):
        return str(self.value)

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        super().__init__(value) 

    @Field.value.setter
    def value(self, new_value):
        if not self.is_valid_phone(new_value):
            raise ValueError("Invalid phone number")
        self._value = new_value

    @staticmethod
    def is_valid_phone(value):
        return isinstance(value, str) and len(value) == 10 and value.isdigit()

class Birthday(Field):
    def __init__(self, value=None):
        super().__init__(value)

    @Field.value.setter
    def value(self, new_value):
        try:
            datetime.strptime(new_value, '%Y-%m-%d')
            self._value = new_value
        except ValueError:
            raise ValueError("Invalid date format for birthday")

class Record:
    def __init__(self, name, phone_numbers=None, birthday=None):
        self.name = Name(name)
        self.phones = []
        self.birthday = Birthday(birthday) if birthday else None
        if phone_numbers:
            for phone_number in phone_numbers:
                self.add_phone(phone_number)
            

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(str(p) for p in self.phones)}, birthday: {self.birthday}"

    def add_phone(self, phone_number):
        phone = Phone(phone_number)
        if phone.value not in [p.value for p in self.phones]:
            self.phones.append(phone)
        else:
            raise ValueError("Phone number already exists in the record")

    def find_phone(self, phone_number):
        for phone in self.phones:
            if phone.value == phone_number:
                return phone
        return None

    def edit_phone(self, old_phone, new_phone):
        phone_obj = self.find_phone(old_phone)
        if phone_obj:
            new_phone_obj = Phone(new_phone)
            if new_phone_obj.value not in [p.value for p in self.phones]:
                phone_obj.value = new_phone_obj.value
            else:
                raise ValueError("New phone number already exists in the record")
        else:
            raise ValueError("Phone number not found in record")

    def remove_phone(self, phone):
        phone_obj = self.find_phone(phone)
        if phone_obj:
            self.phones.remove(phone_obj)
        else:
            raise ValueError("Phone number not found in record")

    def days_to_birthday(self):
        if self.birthday:
            today = datetime.now().date()
            next_birthday = datetime(today.year, *map(int, self.birthday.value.split('-'))).date()
            if today > next_birthday:
                next_birthday = datetime(today.year + 1, *map(int, self.birthday.value.split('-'))).date()
            return (next_birthday - today).days
        return None

class AddressBook(UserDict):
    def __init__(self, file):
        super().__init__()
        self.file = file
        self.record_id = 1
        self.load()

    def add_record(self, record):
        self.data[record.name.value] = record
        self.record_id += 1

    def find(self, query):
        results = []
        for record in self.data.values():
            if query.lower() in record.name.value.lower():
                results.append(record)
            for phone in record.phones:
                if query in phone.value:
                    results.append(record)
        return results

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def iterator(self, batch_size=1):
        records = list(self.data.values())
        for i in range(0, len(records), batch_size):
            yield records[i:i + batch_size]

    def dump(self):
        with open(self.file, 'wb') as file:
            pickle.dump((self.record_id, self.data), file)

    def load(self):
        try:
            with open(self.file, 'rb') as file:
                self.record_id, self.data = pickle.load(file)
        except FileNotFoundError:
            pass

class Controller(cmd.Cmd):
    def __init__(self, address_book):
        super().__init__()
        self.address_book = address_book

    def do_search(self, line):
        """Search for contacts by name or phone number."""
        results = self.address_book.find(line)
        if results:
            for record in results:
                print(record)
        else:
            print("No matching records found.")

    def do_exit(self, line):
        """Exit the program."""
        self.address_book.dump()
        return True


if __name__ == "__main__":
    file_path = "address_book.pkl"
    address_book = AddressBook(file_path)
    controller = Controller(address_book)
    controller.cmdloop("Welcome to the Address Book CLI!")

# Приклад використання
address_book = AddressBook()
record1 = Record("John Doe", phone_numbers=["1234567890"], birthday="1990-05-15")
record2 = Record("Jane Smith", phone_numbers=["5555555555"])

address_book.add_record(record1)
address_book.add_record(record2)

print(address_book.find("John Doe"))
print(address_book.find("Jane Smith"))

record1.edit_phone("1234567890", "9999999999")
print(address_book.find("John Doe"))

record2.remove_phone("5555555555")
print(address_book.find("Jane Smith"))

for batch in address_book.iterator(batch_size=1):
    for record in batch:
        print(record.name, record.days_to_birthday())

