from time import sleep
import re, os, requests
from bs4 import BeautifulSoup as bsp

t = open('gamelinks.txt','r')
try:
    donet = open('donelinks.txt','r')
except:
    donet = open('donelinks.txt','w')
    donet.close()
    donet = open('donelinks.txt','r')
game_links = [x.replace('\n','') for x in t.readlines()]
done_links = [x.replace('\n','') for x in donet.readlines()]
game_links = [x for x in game_links if x not in done_links]
t.close()

def involved(string):
    return([a['href'].split('/')[-1].split('.')[0] for a in string.find_all('a')])

def shot(string):
   inv = involved(string)
   string = string.get_text()
   sting = string.split(' ')
   if 'misses' in sting:
     outcome = 'miss'
     d = sting.index('misses')
   elif 'makes' in sting:
     outcome = 'make'
     d = sting.index('makes')
   try:
       dm = sting.index('from')
   except:
       dm = sting.index('at')
   player = ' '.join(sting[:d]) + ' - ' + inv[0]
   shottype = ' '.join(sting[d+1:dm])
   sing = list(string)
   assister = ''
   blocker = ''
   try:
       action = ''.join(sing[sing.index('('):sing.index(')')]).split()
   except:
       action = ''
       assister = ''
       blocker = ''
   if 'assist' in string:
       am = sting.index("(assist")
       blocker = ''
       dist = ' '.join(sting[dm + 1 :am])[:-3]
       bym = sting.index('by')
       assister = ' '.join(sting[bym+1:]).replace(')','') + ' - ' + inv[1]
   elif 'block' in string:
       assister = ''
       am = sting.index("(block")
       bym = sting.index('by')
       dist = ' '.join(sting[dm + 1 :am])[:-3]
       blocker = ' '.join(sting[bym+1:]).replace(')','') + ' - ' + inv[1]
   else:
       dist = ' '.join(sting[dm + 1:])[:-3]
   if 'rim' in string:
       dist = 0
   return player,shottype,outcome,dist,assister,blocker

def foul(string):
    if 'foul' in string.text:
        inv = involved(string)
        string = string.get_text()
        sting = string.split(' ')
        fm = sting.index('foul')
        ft = ' '.join(sting[:fm]).lower()
        pm = sting.index('by')
        if '(drawn' not in sting:
            byplayer = ' '.join(sting[pm+1:]) + ' - ' + inv[0]
            drawnplayer = ''
        else:
            drm = sting.index('(drawn')
            byplayer = ' '.join(sting[pm+1:drm]) + ' - ' + inv[0]
            drawnplayer = ' '.join(sting[drm+2:]).replace(')','') + ' - ' + inv[1]
        return ft,byplayer,drawnplayer
    else:
        return '','',''

def rebound(string):
    if 'rebound' in string.text:
        inv = involved(string)
        string = string.get_text()
        sting = string.split(' ')
        pm = sting.index('by')
        if len(inv) > 0:
            player = ' '.join(sting[pm+1:]) + ' - ' + inv[0]
        else:
            player = ' '.join(sting[pm+1:])
        rm = sting.index('rebound')
        rt = ' '.join(sting[:rm]).lower()
        return player,rt
    else:
        return '',''

def violation(string):
    if 'Violation' in string.text:
        inv = involved(string)
        string = string.get_text()
        sting = string.split(' ')
        pm = sting.index('by')
        for a in sting:
            if '(' in a:
                cm = sting.index(a)
        if len(inv) > 0:
            player = ' '.join(sting[pm+1:cm]) + ' - ' + inv[0]
        else:
            player = ' '.join(sting[pm+1:cm])
        action = ' '.join(sting[cm:]).replace(')','').replace('(','')
        return player,action

def timeout(string):
    if 'timeout' in string.text:
        return ['!']
    else:
        return ['']

def freethrow(string):
    inv = involved(string)
    string = string.get_text()
    sting = string.split(' ')
    if 'makes' in string:
        action = 'make'
        am = sting.index('makes')
    else:
        action = 'miss'
        am = sting.index('misses')
    player = ' '.join(sting[:am]) + ' - ' + inv[0]
    if 'technical' not in string:
        tm = sting.index('throw')
        ftn = ' '.join(sting[tm+1:])
    else:
        ftn = 'technical'
    return player,action,ftn

def entergame(string):
    inv = involved(string)
    string = string.get_text()
    sting = string.split(' ')
    em = sting.index('enters')
    fr = sting.index('for')
    enterer = ' '.join(sting[:em]) + ' - ' + inv[0]
    leaver = ' '.join(sting[fr+1:]) + ' - ' + inv[1]
    return enterer, leaver

def turnover(string):
    if 'Turnover' in string.text:
        inv = involved(string)
        string = string.get_text()
        sting = string.split(' ')
        bm = sting.index('by')
        cml = [a for a in sting if '(' in a]
        cm = sting.index(cml[0])
        if len(inv) > 0:
            player = ' '.join(sting[bm+1:cm]) + ' - ' + inv[0]
        else:
            player = ' '.join(sting[bm+1:cm])
        sing = list(string)
        p1 = sing.index('(')
        p2 = sing.index(')')
        action = ''.join(sing[p1+1:p2])
        if ';' in action:
            action = action.split('; ')
            turntype = action[0]
            act1 = action[1].split()[0]
            bm = action[1].split().index('by')
            perp = ' '.join(action[1].split()[bm+1:]) + ' - ' + inv[1]
        else:
            turntype = action
            act1 = ''
            perp = ''
        return player,turntype,act1,perp
    else:
        return '','','',''

def jumpball(string):
    if 'Jump ball' in string.text:
        inv = involved(string)
        string = string.get_text()
        sting = string.split()
        bm = sting.index('ball:')
        vsm = sting.index('vs.')
        player1 = ' '.join(sting[bm+1:vsm]) + ' - ' + inv[0]
        sing = list(string)
        p1 = sing.index('(')
        p2 = sing.index(')')
        action = ''.join(sing[p1+1:p2]).split()
        em = sting.index('(' + action[0])
        player2 = ' '.join(sting[vsm+1:em]) + ' - ' + inv[1]
        gm = action.index('gains')
        poss = ' '.join(action[:gm]) + ' - ' + inv[2]
        return player1, player2, poss
    else:
        return '','',''

def timeleft_to_sec(t):
  s = t.index(':')
  s1 = t.index('.')
  min = int(t[:s]) * 60
  sec = int(t[s+1:s1])
  return min + sec

def play_caller(string):
    try:
        is_shot = list(shot(string))
    except:
        is_shot = ['','','','','','']
    try:
        is_foul = list(foul(string))
    except:
        is_foul = ['','','']
    try:
        is_rbd = list(rebound(string))
    except:
        is_rbd = ['','']
    try:
        is_vio = list(violation(string))
    except:
        is_vio = ['','']
    try:
        is_to = list(timeout(string))
    except:
        is_to = ['']
    try:
        is_ft = list(freethrow(string))
    except:
        is_ft = ['','','']
    try:
        is_ent = list(entergame(string))
    except:
        is_ent = ['','']
    try:
        is_turn = list(turnover(string))
    except:
        is_turn = ['','','','']
    try:
        is_jump = list(jumpball(string))
    except:
        is_jump = ['','','']
    return is_shot + is_foul + is_rbd + is_vio + is_to + is_ft + is_ent + is_turn + is_jump

## shooter,shottype,outcome,dist,assister,blocker,foultype,byplayer,drawnplayer,reboundplayer,reboundtype,violplayer,violationtype,timeoutteam,ftshooter,ftoutcome,ftn,enterer,leaver,turnoverplayer,turntype,act1,perp,jbplayer1, jbplayer2, jbposs

def pbp2(link):
    url = 'https://www.basketball-reference.com/boxscores/pbp/' + link.split('/')[-1]
    r = requests.get(url)
    r=r.text
    soup = bsp(r, 'html.parser')
    plays = []
    dog = ' '.join(soup.find('div',class_='scorebox').find('div',class_='scorebox_meta').find('div').get_text().split(', ')[1:]).replace(',','')
    log = soup.find('div',class_='scorebox').find('div',class_='scorebox_meta').find_all('div')[1].get_text().replace(',','')
    tog = soup.find('div',class_='scorebox').find('div',class_='scorebox_meta').find('div').get_text().split(',')[0]
    comment = soup.find(text=re.compile("table_outer_container"))
    com = soup
    awayTeamabbr,homeTeamabbr = [x.split('/')[2] for x in [a['href'] for a in soup.find('div',class_='scorebox').find_all('a') if 'teams' in a['href']]]
    awayFinScore = soup.find_all('div',class_='score')[0].get_text()
    homeFinScore = soup.find_all('div',class_='score')[1].get_text()
    try:
        comment = soup.find(text=re.compile("playoffs"))
        com = bsp(comment, 'html.parser')
        gameType = 'playoff'
    except:
        gameType = 'regular'
    if int(awayFinScore) > int(homeFinScore):
        winningTeam = awayTeamabbr
    elif int(awayFinScore) < int(homeFinScore):
        winningTeam = homeTeamabbr
    #print('read\nplays')
    for i in range(2,len(soup.find('table',id='pbp').find_all('tr'))):
        try:
            time = soup.find('table',id='pbp').find_all('tr')[i].find_all('td')[0].text.replace('\n','')
            awayPlay = soup.find('table',id='pbp').find_all('tr')[i].find_all('td')[1]
            if 'Start of' in awayPlay.text:
                pass
            elif 'End' in awayPlay.text:
                homePlay = ''
                awayScore = plays[-1][10]
                homeScore = plays[-1][-1]
                plays.append([link,gameType,log,dog,tog,winningTeam,q,time,awayTeamabbr,awayPlay,awayScore,homeTeamabbr,homePlay,homeScore])
                q += 1
            elif 'Jump ball' in awayPlay.text:
                awayScore = plays[-1][10]
                homeScore = plays[-1][-1]
                homePlay = ''
                plays.append([link,gameType,log,dog,tog,winningTeam,q,time,awayTeamabbr,awayPlay,awayScore,homeTeamabbr,homePlay,homeScore])
            else:
                awayScore = soup.find('table',id='pbp').find_all('tr')[i].find_all('td')[3].text.replace('\n','').split('-')[0]
                homeScore = soup.find('table',id='pbp').find_all('tr')[i].find_all('td')[3].text.replace('\n','').split('-')[1]
                homePlay = soup.find('table',id='pbp').find_all('tr')[i].find_all('td')[5]
                plays.append([link,gameType,log,dog,tog,winningTeam,q,time,awayTeamabbr,awayPlay,awayScore,homeTeamabbr,homePlay,homeScore])
        except:
            try:
                if len(plays) == 0:
                    q = 1
                    time = soup.find('table',id='pbp').find_all('tr')[i].find_all('td')[0].text.replace('\n','')
                    jb = soup.find('table',id='pbp').find_all('tr')[i].find_all('td')[1]
                    plays.append([link,gameType,log,dog,tog,winningTeam,q,time,awayTeamabbr,jb,0,homeTeamabbr,'',0])
            except:
                pass
    if plays[-1][7] != '0:00.0' and plays[-1][9] == '' and plays[-1][12] == '':
        plays[-1][9] = 'End of Game'
    else:
        plays.append([link,gameType,log,dog,tog,winningTeam,q,'0:00.0',awayTeamabbr,'End of Game',awayScore,homeTeamabbr,'',homeScore])
    plays[-1][6]-=1
    return plays

def breakdown(plays):
    broke = []
    for play in plays:
      if play[12] == '' or play[12].text.encode('ascii','ignore').decode() == '':
        broke.append(play + play_caller(play[9]))
      else:
        broke.append(play + play_caller(play[12]))
    for i in range(len(broke)):
        try:
          broke[i][9] = broke[i][9].text.encode('ascii','ignore').decode()
          broke[i][12] = broke[i][12].text.encode('ascii','ignore').decode()
        except:
          pass
    for brek in broke:
        brek[7] = timeleft_to_sec(brek[7])
        if brek[-13] == '!':
            if brek[9] != '':
                brek[-13] = brek[8]
            else:
                brek[-13] = brek[11]
    return broke

y = open('output_pbp.csv','a')
if os.stat('output_pbp.csv').st_size == 0:
    y.write('URL,GameType,Location,Date,Time,WinningTeam,Quarter,SecLeft,AwayTeam,AwayPlay,AwayScore,HomeTeam,HomePlay,HomeScore,Shooter,ShotType,ShotOutcome,ShotDist,Assister,Blocker,FoulType,Fouler,Fouled,Rebounder,ReboundType,ViolationPlayer,ViolationType,TimeoutTeam,FreeThrowShooter,FreeThrowOutcome,FreeThrowNum,EnterGame,LeaveGame,TurnoverPlayer,TurnoverType,TurnoverCause,TurnoverCauser,JumpballAwayPlayer,JumpballHomePlayer,JumpballPoss')

t = 1
used_links = []
for link in game_links:
   if t % 15 ==0 and t != 0:
      print('Sleeping...')
      try:
        sleep(20)
      except:
         b = open('gamelinks.txt','w')
         for link in list(set(game_links) - set(used_links)):
             b.write(link + '\n')
         b.close()
         c = open('donelinks.txt','a')
         for link in used_links:
             c.write(link + '\n')
         c.close()
         y.close()
         break
   try:
      bd = breakdown(pbp2(link))
      for play in bd:
        y.write('\n'+','.join([str(d) for d in play]))
      used_links.append(link)
      print(str(len(game_links) - len(used_links) +1) + ' -- ' + link)
      sleep(3)
      t+=1
      if link == game_links[-1]:
          b = open('gamelinks.txt','w')
          b.close()
          c = open('donelinks.txt','a')
          for link in used_links:
              c.write(link + '\n')
          c.close()
   except:
      b = open('gamelinks.txt','w')
      for link in list(set(game_links) - set(used_links)):
          b.write(link + '\n')
      b.close()
      c = open('donelinks.txt','a')
      for link in used_links:
          c.write(link + '\n')
      c.close()
      y.close()
      break
