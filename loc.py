import pickle
from os.path import exists

from geopy.distance import geodesic
from geopy.geocoders import Nominatim
import pandas as pd
import telebot


class Location:
    def __init__(self):
        self.geolocator = Nominatim(user_agent='main_app')
        if exists('loc.pkl'):
            with open('loc.pkl', mode='rb') as f:
                self.d = pickle.load(f)
        else:
            self.d = dict()
        self.my_loc = 'Россия Полевской Городской округ Полевской Декабристов 22'
        self.adr_srt, self.adr_dict, self.locas = set(), dict(), None
        self.done_df, self.task_df = None, None
        self.bot = telebot.TeleBot('1551764899:AAExHBckU96VmJHkZt9OTAo4Xb0UGKj6c58')

    def text2loc(self, place: str):
        if place not in self.d:
            locations = self.geolocator.geocode(place, timeout=1)
            print(locations.address)
            self.d[place] = locations.latitude, locations.longitude
        return self.d[place]

    def build_route(self, lst):
        for item in lst:
            if item[0]:
                self.adr_srt.add(item[0])
                if item[0] in self.adr_dict:
                    self.adr_dict[item[0]].append(item[1])
                else:
                    self.adr_dict[item[0]] = [item[1]]
            else:
                self.adr_srt.add(item[1])
        print(self.adr_srt, self.adr_dict, sep='\n')
        start = self.text2loc(self.my_loc)
        self.locas = sorted([(item, geodesic(start, self.text2loc(item)).km) for item in self.adr_srt],
                            key=lambda x: x[1], reverse=True)
        print(self.locas)

    def __del__(self):
        with open('loc.pkl', mode='wb') as f:
            pickle.dump(self.d, f)

    def go(self):
        print('\nМаршрут построен: ')
        print('\t', end='')
        print('\n\t'.join([item[0] for item in self.locas]))
        while self.locas:
            # print(f'Пункт: {self.locas[-1][0]}')
            self.bot.send_message(911336813, text=f'{self.locas[-1][0]}')
            # input('>>>>>')
            start = self.locas.pop()[0]
            st1 = self.text2loc(start)

            if start in self.adr_dict:
                self.locas.extend(self.adr_dict[start])
                self.adr_dict.pop(start)
            self.locas = [item[0] if isinstance(item, tuple) else item for item in self.locas]
            self.locas = sorted([(item, geodesic(st1, self.text2loc(item)).km) for item in self.locas],
                                key=lambda x: x[1], reverse=True)
            # print(self.locas)

    def file2lst(self, path):
        self.task_df = pd.read_excel(path, sheet_name='Task')
        self.task_df = self.task_df.astype('object')
        self.done_df = pd.read_excel(path, sheet_name='Done')
        self.done_df = self.done_df.astype('object')
        self.task_df.fillna('', inplace=True)
        self.done_df.fillna('', inplace=True)
        ddf = self.task_df.loc[:, ['From', 'For']].to_dict()
        result = []
        for i in ddf['From'].keys():
            result.append((ddf['From'][i], ddf['For'][i]))
        return result


if __name__ == '__main__':
    loc = Location()
    adr = loc.file2lst('location.xlsx')
    loc.build_route(adr)
    loc.go()
    del loc
