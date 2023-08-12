from urllib.request import Request, urlopen
import datetime
import re
from bs4 import BeautifulSoup
import pandas as pd
import requests
from tabulate import tabulate

class mlb():

    def __init__(self):

        self.dic_team_name_id = {
                "arizona-diamondbacks":29,"atlanta-braves":15,"baltimore-orioles":1,"boston-red-sox":2,
                "chicago-cubs":16,"chicago-white-sox":4,"cincinnati-reds":17,"cleveland-guardians":5,
                "colorado-rockies":27,"detroit-tigers":6,"houston-astros":18,"kansas-city-royals":7,
                "los-angeles-angels":3,"los-angeles-dodgers":19,"miami-marlins":28,"milwaukee-brewers":8,
                "minnesota-twins":9,"new-york-mets":21,"new-york-yankees":10,"oakland-athletics":11,
                "philadelphia-phillies":22,"pittsburgh-pirates":23,"san-diego-padres":25,"san-francisco-giants":26,
                "seattle-mariners":12,"st-louis-cardinals":24,"tampa-bay-rays":30,"texas-rangers":13,"toronto-blue-jays":14,
                "washington-nationals":20
                }

        self.dic_team_nikname = {
                "ATL":"atlanta-braves","ARI":"arizona-diamondbacks","BAL":"baltimore-orioles","BOS":"boston-red-sox",
                "CHC":"chicago-cubs","CHW":"chicago-white-sox","CIN":"cincinnati-reds","CLE":"cleveland-guardians",
                "COL":"colorado-rockies","DET":"detroit-tigers","HOU":"houston-astros","KC":"kansas-city-royals",
                "LAA":"los-angeles-angels","LAD":"los-angeles-dodgers","MIA":"miami-marlins","MIL":"milwaukee-brewers",
                "MIN":"minnesota-twins","NYM":"new-york-mets","NYY":"new-york-yankees","OAK":"oakland-athletics",
                "PHI":"philadelphia-phillies","PIT":"pittsburgh-pirates","SD":"san-diego-padres","SF":"san-francisco-giants",
                "SEA":"seattle-mariners","STL":"st-louis-cardinals","TB":"tampa-bay-rays","TEX":"texas-rangers",
                "TOR":"toronto-blue-jays","WSH":"washington-nationals"
                }

    def get_games_results(self, date):
        self.url_games = f'https://www.espn.com/mlb/schedule/_/date/{date}'
        self.games = requests.get(self.url_games, headers={'User-Agent': 'Mozilla/5.0'}) #For avoid HTPP Erro 403 Forbidden we use headers parameter
        self.soup_games =  BeautifulSoup(self.games.text, 'html.parser')

        tables_games_results = self.soup_games.find_all('table')
        self.dic_games = {}
        self.url_stats = []

        if tables_games_results:
            self.table = self.soup_games.find_all('table')[0] 
            self.divs_team1 = self.table.find_all('div', attrs={'class': 'matchTeams'})
            self.divs_team2 = self.table.find_all('div', attrs={'class': 'local'})
            self.tds = self.table.find_all('td', attrs={'class': 'teams__col Table__TD'})

            self.len = len(self.divs_team1)

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
                    
                    self.list_data_game.append(game_result)

                    #--------- Geting the score and Nick Names for team1 and team2 -------
                    self.list_results = game_result.split(',')
                    
                    self.result_team1 =  re.search("\d+", self.list_results[0]).group()
                    self.result_team2 =  re.search("\d+", self.list_results[1]).group()
                    
                    self.nickname_team1 =  re.search("\w+", self.list_results[0]).group()
                    self.nickname_team2 =  re.search("\w+", self.list_results[1]).group()
                    #-------------------------------------------------------------------
                    
                    #Getting the tag a element for the Pitcher who won and who loss
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

                        if int(self.result_team1) > int(self.result_team2):
                            name_team1 = self.dic_team_nikname[self.nickname_team1]
                            id_team_winner = self.dic_team_name_id[name_team1]
                        else:
                            name_team2 = self.dic_team_nikname[self.nickname_team2]
                            id_team_winner = self.dic_team_name_id[name_team2]
                        
                        id_pitch_losser = self.tds[j + 2].find('a').get('href').split('/')[-1]
                        url_pitch_losser_stats = f'https://www.espn.com/mlb/player/batvspitch/_/id/{id_pitch_losser}/teamId/{id_team_winner}'
                        self.url_stats.append(url_pitch_losser_stats)
                        self.dic_games[f'Game_{i}'] = self.list_data_game
                    
                    elif loss == None:
                        loss = ''
                        self.list_data_game.append(win.text)
                        self.list_data_game.append(loss)

                        if int(self.result_team1) > int(self.result_team2):
                            name_team2 = self.dic_team_nikname[self.nickname_team2]
                            id_team_losser = self.dic_team_name_id[name_team2]
                        else:
                            name_team1 = self.dic_team_nikname[self.nickname_team1]
                            id_team_losser = self.dic_team_name_id[name_team1]

                        id_pitch_winner = self.tds[j + 1].find('a').get('href').split('/')[-1]
                        url_pitch_winner_stats = f'https://www.espn.com/mlb/player/batvspitch/_/id/{id_pitch_winner}/teamId/{id_team_losser}'
                        self.url_stats.append(url_pitch_winner_stats)
                        self.dic_games[f'Game_{i}'] = self.list_data_game
                    
                    else:
                        self.list_data_game.append(win.text)
                        self.list_data_game.append(loss.text)
                        
                        if int(self.result_team1) > int(self.result_team2):
                            name_team1 = self.dic_team_nikname[self.nickname_team1]
                            id_team_winner = self.dic_team_name_id[name_team1]
                            name_team2 = self.dic_team_nikname[self.nickname_team2]
                            id_team_losser = self.dic_team_name_id[name_team2]
                        else:
                            name_team1 = self.dic_team_nikname[self.nickname_team1]
                            id_team_losser = self.dic_team_name_id[name_team1]
                            name_team2 = self.dic_team_nikname[self.nickname_team2]
                            id_team_winner = self.dic_team_name_id[name_team2]

                        self.dic_games[f'Game_{i}'] = self.list_data_game

                        id_pitch_winner = self.tds[j + 1].find('a').get('href').split('/')[-1]
                        id_pitch_losser = self.tds[j + 2].find('a').get('href').split('/')[-1]
                        
                        url_pitch_winner_stats = f'https://www.espn.com/mlb/player/batvspitch/_/id/{id_pitch_winner}/teamId/{id_team_losser}'
                        self.url_stats.append(url_pitch_winner_stats)
                        url_pitch_losser_stats = f'https://www.espn.com/mlb/player/batvspitch/_/id/{id_pitch_losser}/teamId/{id_team_winner}'
                        self.url_stats.append(url_pitch_losser_stats)

                j += 4 #For acces to the td that is in the next row of the table for next lap of the loop
        
        self.dic_games['urls_stats'] = self.url_stats
        
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
                self.html_table = re.sub(r'0\.', '.', str(self.html_table))
                # print(self.html_table)

                self.stats_title = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}) #For avoid HTPP Erro 403 Forbidden we use headers parameter
                self.soup_sts =  BeautifulSoup(self.stats_title.text, 'html.parser')
                self.title = self.soup_sts.find('div', attrs={'class': 'Table__Title'}).text
                
                self.dic_stats[f'sts{i}'] = {'title': self.title, 'stats_data': self.html_table, 'id': i}

            except Exception as e:
                self.dic_stats[f'sts{i}'] = {'title': 'There is no data available', 'stats_data': '', 'id': i}
                print(e)
                continue

            finally:
                i += 1

        return self.dic_stats
    

if __name__ == '__main__':
    mlb1 =  mlb()

    # date =  datetime.datetime.now().strftime('%Y%m%d')
    # games = mlb1.get_games_results('20220428') #20220527 20220423
    # for game in games:
    #     print(games[game])

    # print('The URLS list for the statistics are bellow:')
    # print(mlb1.url_stats)
    
    urls = ['https://www.espn.com/mlb/player/batvspitch/_/id/40921/david-peterson']

    stats = mlb1.get_stats(urls)

    # print(stats)
    

#===================================================================================================================================




