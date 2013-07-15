# The MIT License (MIT)
# 
# Copyright (c) 2013 Daigo Tanaka (@daigotanaka)
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import codecs
import csv
import os
import re

from libs import Os


class AddressBook(Os):

    def __init__(self, user, file):
        self.nickname_field = "Nickname"
        self.primary_phone_field = "Phone 1 - Value"
        self.file = file
        self.book = {}
        if not os.path.exists(file):
            raise Exception("Address book file not found")

        data = codecs.open(file, "rU", "utf-16")
        reader = csv.reader(data)
        count = 0
        err = True
        while err:
            try:
                for row in reader:
                    if count == 0:
                        self.fields = row
                    nickname = row[self.fields.index(self.nickname_field)].lower()
                    if not nickname:
                        continue
                    self.book[nickname] = row
                    count += 1
            except UnicodeError:
                err = True
                continue
            err = False
        super(AddressBook, self).__init__(user)

    def get_field_index(self, field_name):
        return self.fields.index(field_name)

    def get_row(self, nickname):
        return self.book.get(nickname, None)

    def get_primary_phone(self, nickname):
        row = self.get_row(nickname)
        if not row:
            return None
        raw_phone = row[self.get_field_index(self.primary_phone_field)]
        number = re.sub("\D", "", raw_phone)
        return number
 
if __name__ == "__main__":
    addressbook = AddressBook("pi", "./addressbook.csv")
    info = addressbook.get_primary_phone("my wife")
    print info
