from urllib.request import Request, urlopen
import datetime
import re
from bs4 import BeautifulSoup
import pandas as pd
import requests
from tabulate import tabulate

class mlb():

    def __init__(self):
        self.dic_team_name_id = {}
        
        with open('team_id.txt', 'r') as file:
            for line in file:
                line = line.split(':')
                self.team_name = line[0]
                self.team_id = line[1].replace('\n', '')
                self.dic_team_name_id[self.team_name] = self.team_id

    def get_games_results(self, date):
        self.url_games = f'https://www.espn.com/mlb/schedule/_/date/{date}'
        self.games = requests.get(self.url_games, headers={'User-Agent': 'Mozilla/5.0'}) #For avoid HTPP Erro 403 Forbidden we use headers parameter
        self.soup_games =  BeautifulSoup(self.games.text, 'html.parser')

        tables_games_results = self.soup_games.find_all('table')
        self.dic_games = {}

        if tables_games_results:
            self.table = self.soup_games.find_all('table')[0] 
            self.divs_team1 = self.table.find_all('div', attrs={'class': 'matchTeams'})
            self.divs_team2 = self.table.find_all('div', attrs={'class': 'local'})
            self.tds = self.table.find_all('td', attrs={'class': 'teams__col Table__TD'})

            self.len = len(self.divs_team1)
            self.url_stats.clear()#Cleaning the previous data in the list self.url_stats

            j = 0 #for iterate tds elements
            for i in range(self.len):
                self.list_data_game = []

                team1 = self.divs_team1[i].find('a').get('href').split('/')[-1]
                self.list_data_game.append(team1)

                team2 = self.divs_team2[i].find('a').get('href').split('/')[-1]
                self.list_data_game.append(team2)
                
                game_result = self.tds[j].find('a').text

                if game_result == 'Postponed': 
                    result, win, loss = 'Postponed', '', ''
                    self.list_data_game.append(result)
                    self.list_data_game.append(win)
                    self.list_data_game.append(loss)
                    self.dic_games[f'Game_{i}'] = self.list_data_game

                else: 
                    result = self.tds[j].find('a').text
                    self.list_data_game.append(result)

                    win = self.tds[j + 1].find('a')
                    loss = self.tds[j + 2].find('a')

                    if win == None and loss == None:
                        loss ,win = '', ''
                        self.list_data_game.append(win)
                        self.list_data_game.append(loss)
                        self.dic_games[f'Game_{i}'] = self.list_data_game

                    elif win == None:
                        win = ''
                        self.list_data_game.append(win)
                        self.list_data_game.append(loss.text)
                        self.dic_games[f'Game_{i}'] = self.list_data_game
                        # id_pitch2 = self.tds[j + 2].find('a').get('href').split('/')[-1]
                        # id_team1 = self.dic_team_name_id[team1]
                        # url_pitch2_stats = f'https://www.espn.com/mlb/player/batvspitch/_/id/{id_pitch2}/teamId/{id_team1}'
                        # self.url_stats.append(url_pitch2_stats)
                    
                    elif loss == None:
                        loss = ''
                        self.list_data_game.append(win.text)
                        self.list_data_game.append(loss)
                        self.dic_games[f'Game_{i}'] = self.list_data_game
                    
                    else:
                        self.list_data_game.append(win.text)
                        self.list_data_game.append(loss.text)
                        self.dic_games[f'Game_{i}'] = self.list_data_game

                        id_pitch1 = self.tds[j + 1].find('a').get('href').split('/')[-1]
                        id_team1 = self.dic_team_name_id[team1]
                        id_pitch2 = self.tds[j + 2].find('a').get('href').split('/')[-1]
                        id_team2 = self.dic_team_name_id[team2]
                        
                        url_pitch1_stats = f'https://www.espn.com/mlb/player/batvspitch/_/id/{id_pitch1}/teamId/{id_team2}'
                        self.url_stats.append(url_pitch1_stats)
                        url_pitch2_stats = f'https://www.espn.com/mlb/player/batvspitch/_/id/{id_pitch2}/teamId/{id_team1}'
                        self.url_stats.append(url_pitch2_stats)

                j += 4 #For acces to the td that is in the next row of the table for next lap of the loop
            
        return self.dic_games

    def get_games(self, date):        
        self.url_games = f'https://www.espn.com/mlb/schedule/_/date/{date}'
        self.games = requests.get(self.url_games, headers={'User-Agent': 'Mozilla/5.0'}) #For avoid HTPP Erro 403 Forbidden we use headers parameter
        self.soup_games =  BeautifulSoup(self.games.text, 'html.parser')
        
        table_games = self.soup_games.find_all('table')
        self.dic_games = {}
        self.url_sts_games = []
        
        if table_games:
            self.table = table_games[0] 
            self.divs_team1 = self.table.find_all('div', attrs={'class': 'matchTeams'})
            self.divs_team2 = self.table.find_all('div', attrs={'class': 'local'})
            self.td_pitchs = self.table.find_all('td', attrs={'class': 'probable__col Table__TD'})

            self.len = len(self.divs_team1)

            for i in range(self.len):
                self.list_data_game = []

                team1 = self.divs_team1[i].find('a').get('href').split('/')[-1]
                self.list_data_game.append(team1)

                team2 = self.divs_team2[i].find('a').get('href').split('/')[-1]
                self.list_data_game.append(team2)
                
                tag_p = self.td_pitchs[i].find('p')

                if tag_p == None: #This happen when there is not tag 'p' (inside tag p are tags 'a' and tag 'span')
                    pitch_match = ''
                    self.list_data_game.append(pitch_match)
                    self.dic_games[f'Game_{i}'] = self.list_data_game

                else: #This means that we found a tag 'p' where are one or two tags 'a' and one tag 'span'
                    tags_a = tag_p.find_all('a')
                    tag_span = tag_p.find('span')

                    if len(tags_a) < 2: #If only found one tag 'a'

                        spans = tag_p.find_all('span')
                        
                        if spans[0].text == 'Undecided':
                            pitch_match = spans[0].text + ' vs ' + tags_a[0].text
                            self.list_data_game.append(pitch_match)

                            id_team1 = self.dic_team_name_id[team1]
                            id_pitch2 = tags_a[0].get('href').split('/')[-1]

                            url_pitch2_stats = f'https://www.espn.com/mlb/player/batvspitch/_/id/{id_pitch2}/teamId/{id_team1}'
                            self.url_sts_games.append(url_pitch2_stats)
                        
                        elif spans[1].text == 'Undecided':
                            pitch_match =  tags_a[0].text + ' vs ' + spans[1].text
                            self.list_data_game.append(pitch_match)

                            id_team2 = self.dic_team_name_id[team2]
                            id_pitch1 = tags_a[0].get('href').split('/')[-1]

                            url_pitch2_stats = f'https://www.espn.com/mlb/player/batvspitch/_/id/{id_pitch1}/teamId/{id_team2}'
                            self.url_sts_games.append(url_pitch2_stats)
                        
                        self.dic_games[f'Game_{i}'] = self.list_data_game
                    
                    else: #It means that we found 2 tags 'a'
                        pitch_match = tags_a[0].text + tag_span.text + tags_a[1].text
                
                        self.list_data_game.append(pitch_match)
                        self.dic_games[f'Game_{i}'] = self.list_data_game

                        id_pitch1 = tags_a[0].get('href').split('/')[-1]
                        id_team1 = self.dic_team_name_id[team1]
                        id_pitch2 = tags_a[1].get('href').split('/')[-1]
                        id_team2 = self.dic_team_name_id[team2]
                        
                        url_pitch1_stats = f'https://www.espn.com/mlb/player/batvspitch/_/id/{id_pitch1}/teamId/{id_team2}'
                        self.url_sts_games.append(url_pitch1_stats)
                        url_pitch2_stats = f'https://www.espn.com/mlb/player/batvspitch/_/id/{id_pitch2}/teamId/{id_team1}'
                        self.url_sts_games.append(url_pitch2_stats)

        self.dic_games['urls_stats'] = self.url_sts_games
        return self.dic_games

    def create_dic_team_id(self):
        self.dic_team_name_id = {}
        with open('team_id.txt', 'r') as file:
            for line in file:
                line = line.split(':')
                self.team_name = line[0]
                self.team_id = line[1].replace('\n', '')
                self.dic_team_name_id[self.team_name] = self.team_id
        
        return self.dic_team_name_id

    def get_stats(self, url_stats):
        #Bellow is an example url format that this function need to receive
        # self.url_stats = 'https://www.espn.com/mlb/player/batvspitch/_/id/41233/teamId/2'

        self.dic_stats = {}

        i = 0
        for url in url_stats:
            try:
                self.req_sts = Request(url, headers={'User-Agent': 'Mozilla/5.0'}) #For avoid HTPP Erro 403 Forbidden we use headers parameter
                self.webpage = urlopen(self.req_sts).read()
                self.df_stats = pd.read_html(self.webpage)

                self.html_table = tabulate(self.df_stats[1], headers='keys', tablefmt='html', floatfmt=".3f")

                self.stats_title = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}) #For avoid HTPP Erro 403 Forbidden we use headers parameter
                self.soup_sts =  BeautifulSoup(self.stats_title.text, 'html.parser')
                self.title = self.soup_sts.find('div', attrs={'class': 'Table__Title'}).text
                
                self.dic_stats[f'sts{i}'] = {'title': self.title, 'stats_data': self.html_table, 'id': i}

            except Exception as e:
                print(e)
                continue

            finally:
                i += 1

        return self.dic_stats
    

if __name__ == '__main__':
    mlb1 =  mlb()

    # date =  datetime.datetime.now().strftime('%Y%m%d')
    # games = mlb1.get_games_results('20220201') #20220527 20220423
    # for game in games:
    #     print(games[game])

    # print('The URLS list for the statistics are bellow:')
    # print(mlb1.url_stats)
    
    urls = ['https://www.espn.com/mlb/player/batvspitch/_/id/40921/david-peterson']

    stats = mlb1.get_stats(urls)

    print(stats)
    

#===================================================================================================================================




