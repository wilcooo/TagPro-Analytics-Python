"""
tagpr_analytics : read raw match data from TagPro Analytics (tagpro.eu)

MIT License

Copyright (c) 2018, Ko

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.



The original license of the PHP code that this project is based on had the
condition that its license should be retained. Following is the license of the
original PHP code by Jeroen van der Gun, hosted on https://tagpro.eu/?science
I don't know wheather a completely rewritten distribution counts as a
'redistribution of source code', but I included it just in case it is.
The original code only consisted of the classes 'LogReader', 'PlayerLogReader',
'MapLogReader' and 'SplatLogReader'. All other classes and functions are made
by me (so only the MIT license above applies)



BSD 2-Clause License

Copyright (c) 2017, Jeroen van der Gun
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

from base64 import b64decode

class LogReader:
    
    __pos = 0
    
    def __init__(self, data):
        self.__data = data
    
    def _end(self):
        return self.__pos >> 3 >= len(self.__data)
    
    def _readBool(self):
        result = 0 if self._end() else self.__data[self.__pos >> 3] >> 7 - (self.__pos & 7) & 1
        self.__pos += 1
        return result
    
    def _readFixed(self, bits):
        result = 0
        for _ in range(bits):
            result = result << 1 | self._readBool()
        return result
    
    def _readTally(self):
        result = 0
        while self._readBool():
            result += 1
        return result
    
    def _readFooter(self):
        size = self._readFixed(2) << 3
        free = 8 - (self.__pos & 7) & 7
        size |= free
        minimum = 0
        while free < size:
            minimum += 1 << free
            free += 8
        return self._readFixed(size) + minimum
    
class PlayerReader(LogReader):
    
    def _joinEvent(self, time, newTeam): pass
    def _quitEvent(self, time, oldFlag, oldPowers, oldTeam): pass
    def _switchEvent(self, time, oldFlag, powers, newTeam): pass
    def _grabEvent(self, time, newFlag, powers, team): pass
    def _captureEvent(self, time, oldFlag, powers, team): pass
    def _flaglessCaptureEvent(self, time, flag, powers, team): pass
    def _powerupEvent(self, time, flag, powerUp, newPowers, team): pass
    def _duplicatePowerupEvent(self, time, flag, powers, team): pass
    def _powerdownEvent(self, time, flag, powerDown, newPowers, team): pass
    def _returnEvent(self, time, flag, powers, team): pass
    def _tagEvent(self, time, flag, powers, team): pass
    def _dropEvent(self, time, oldFlag, powers, team): pass
    def _popEvent(self, time, powers, team): pass
    def _startPreventEvent(self, time, flag, powers, team): pass
    def _stopPreventEvent(self, time, flag, powers, team): pass
    def _startButtonEvent(self, time, flag, powers, team): pass
    def _stopButtonEvent(self, time, flag, powers, team): pass
    def _startBlockEvent(self, time, flag, powers, team): pass
    def _stopBlockEvent(self, time, flag, powers, team): pass
    def _endEvent(self, time, flag, powers, team): pass
    
    NO_TEAM = 0
    RED_TEAM = 1
    BLUE_TEAM = 2
    
    NO_FLAG = 0
    OPPONENT_FLAG = 1
    OPPONENT_POTATO_FLAG = 2
    NEUTRAL_FLAG = 3
    NEUTRAL_POTATO_FLAG = 4
    TEMPORARY_FLAG = 5
    
    NO_POWER = 0
    JUKE_JUICE_POWER = 1
    ROLLING_BOMB_POWER = 2
    TAG_PRO_POWER = 4
    TOP_SPEED_POWER = 8
    
    """
    To update this list of flair when new flair have come out, you can run the
    following code in the JavaScript console of any profile page such as
    http://tagpro-radius.koalabeast.com/profile/52d14bc31c0f1b1421278ab3/
    
    A list of all flair will be printed in the JS console, and in the right
    (python) format to be directly copypastad hereunder.
    
    ***START OF JS CODE***
        
        flair_list = []
        
        for (flair of document.querySelectorAll('#all-flair .flair-list .flair-item')) {
            flair_list.push( {
                namex: name,
                name:           flair.querySelector('.flair-header').innerHTML.trim(),
                description:    flair.querySelector('.flair-description').innerHTML.trim(),
                type:           flair.querySelector('.flair-type').innerHTML.trim(),
                id:             1 - parseInt(flair.querySelector('.flair').style.backgroundPositionX)/16
                                  - parseInt(flair.querySelector('.flair').style.backgroundPositionY),
            } )
        }
        
        flair_list.sort( (a,b) => a.id - b.id )
        
        output = "    FLAIR = {\n            -1: {'name': 'Unknown Flair', 'description': 'Please update the tagpro_analytics module with this flair', 'type': 'special'},\n            0: {'name': 'No Flair', 'description': 'Don\'t show any flair', 'type': 'special'},\n"
        
        for (flair of flair_list) output += '            '+flair.id+": {'name': '"+flair.name.replace("'","\\'")+"', 'description': '"+flair.description.replace("'","\\'")+"', 'type': '"+flair.type.replace("'","\\'")+"'},\n"
        
        console.log(output + "        }")
    
    ***END OF JS CODE***
    """
    
    FLAIR = {
            -1: {'name': 'Unknown Flair', 'description': 'Please update the tagpro_analytics module with this flair', 'type': 'special'},
            0: {'name': 'No Flair', 'description': 'Don\'t show any flair', 'type': 'special'},
            1: {'name': 'Daily Leader Board Winner', 'description': 'Topped the daily leaderboard', 'type': 'boards'},
            2: {'name': 'Weekly Leader Board Winner', 'description': 'Topped the weekly leaderboard', 'type': 'boards'},
            3: {'name': 'Monthly Leader Board Winner', 'description': 'Topped the monthly leaderboard', 'type': 'boards'},
            4: {'name': 'Good Win Rate', 'description': 'Achieved 55% win rate for 300 games', 'type': 'winRate'},
            5: {'name': 'Awesome Win Rate', 'description': 'Achieved 65% win rate for 300 games', 'type': 'winRate'},
            6: {'name': 'Insane Win Rate', 'description': 'Achieved 75% win rate for 300 games', 'type': 'winRate'},
            7: {'name': 'Moderator', 'description': 'This player moderates TagPro', 'type': 'special'},
            8: {'name': 'Map Tester', 'description': 'A difficult job', 'type': 'special'},
            17: {'name': 'Community Contributor', 'description': 'Awarded to recognize players who have gone above and beyond to help the community', 'type': 'special'},
            18: {'name': 'Level 1 Donor', 'description': 'This player has donated $10 to TagPro', 'type': 'special'},
            19: {'name': 'TagPro Developer', 'description': 'Given to TagPro Developers', 'type': 'special'},
            20: {'name': 'Level 2 Donor', 'description': 'This player has donated $40 to TagPro', 'type': 'special'},
            21: {'name': 'Level 3 Donor', 'description': 'This player has donated $100 to TagPro', 'type': 'special'},
            22: {'name': 'Community Contest Winner', 'description': 'Awarded to special contest winners', 'type': 'special'},
            23: {'name': 'Kongregate', 'description': 'Thanks for winning 30 games and reviewing on Kongregate', 'type': 'special'},
            24: {'name': 'Level 4 Donor', 'description': 'This player has donated $200 to TagPro', 'type': 'special'},
            25: {'name': 'Bitcoin Donor (Any Amount)', 'description': 'This player donated BTC to TagPro', 'type': 'special'},
            33: {'name': 'Happy Birthday TagPro', 'description': 'Awarded for TagPro\'s 1st birthday', 'type': 'event'},
            34: {'name': 'Lucky You', 'description': 'Hattrick for a new hat', 'type': 'event'},
            35: {'name': 'How Foolish', 'description': 'You\'re a square', 'type': 'event'},
            36: {'name': 'Hare Today, Goon Tomorrow', 'description': 'Awarded Easter 2014', 'type': 'event'},
            37: {'name': 'UnfortunateSniper Hacks TagPro', 'description': 'TagProAndLuckySpammerSucksAndUnfortunateSniperIsAwesome', 'type': 'event'},
            38: {'name': 'So Very Scary', 'description': 'Played zombie mode in 2014', 'type': 'event'},
            39: {'name': 'Daryl Would Be Proud', 'description': 'Survived zombie mode in 2014', 'type': 'event'},
            40: {'name': 'Happy 2nd Birthday TagPro', 'description': 'Awarded for TagPro\'s 2nd birthday', 'type': 'event'},
            41: {'name': 'Tower 1-1 Complete', 'description': 'Climbed to the top of the TagPro tower', 'type': 'event'},
            42: {'name': 'Good and Lucky', 'description': 'Awarded for St. Patrick\'s Day 2015', 'type': 'event'},
            43: {'name': 'Clowning Around Gravity', 'description': 'April Fools 2015', 'type': 'event'},
            44: {'name': 'Football', 'description': 'Eggball 2017 - Real Football', 'type': 'event'},
            45: {'name': 'Soccer Ball', 'description': 'Eggball 2017 - Fake Football', 'type': 'event'},
            49: {'name': 'Racing For Eggs', 'description': 'Played Easter event in 2015', 'type': 'event'},
            50: {'name': 'Racing For Carrots', 'description': 'Raced for the carrot during Easter 2015', 'type': 'event'},
            51: {'name': 'All balls are created equal!', 'description': 'Supreme Court rules in favor of nationwide gay marriage', 'type': 'event'},
            52: {'name': 'Easy as Pumpkin Pie', 'description': 'Played in zombie event 2015', 'type': 'event'},
            53: {'name': 'Lighter Than a Duck', 'description': '2015 zombie mode survivor', 'type': 'event'},
            54: {'name': 'DOOT DOOT', 'description': 'Good bones and calcium will come to you', 'type': 'event'},
            55: {'name': 'Happy 3rd Birthday TagPro', 'description': 'Awarded for TagPro\'s 3rd Birthday', 'type': 'event'},
            56: {'name': 'Tower 1-2 Complete', 'description': 'But our princess is in another castle', 'type': 'event'},
            57: {'name': 'Pup Drunk', 'description': 'TagPro celebrates St Patrick\'s Day', 'type': 'event'},
            58: {'name': 'Participation Egg', 'description': 'Awarded for TagPro\'s 2016 Easter event', 'type': 'event'},
            59: {'name': 'Valued Member Egg', 'description': 'Dank Sniper', 'type': 'event'},
            65: {'name': 'Bounty Hunter Egg', 'description': 'Sniiiiiiiped!', 'type': 'event'},
            66: {'name': 'Really? Another Pumpkin?', 'description': 'Played in zombie event 2016', 'type': 'event'},
            67: {'name': 'MMM... Brains', 'description': 'It’s not that bad when fried', 'type': 'event'},
            68: {'name': 'Backstabber', 'description': 'How can you live with yourself?', 'type': 'event'},
            69: {'name': 'Cheap Christmas Candy', 'description': 'Common Christmas 2016 present', 'type': 'event'},
            70: {'name': 'You Could Catch Me!', 'description': 'Rare Christmas 2016 present', 'type': 'event'},
            71: {'name': 'Ho! Ho! Ho!', 'description': 'Coveted Christmas 2016 present', 'type': 'event'},
            72: {'name': 'Happy 4th Birthday TagPro', 'description': 'Awarded for TagPro\'s 4th Birthday', 'type': 'event'},
            73: {'name': 'Tower 1-3 Complete', 'description': 'It\'s on like Donkey Kong', 'type': 'event'},
            74: {'name': 'WOAH! It\'s real!', 'description': '$%#!... this is impossible.', 'type': 'event'},
            75: {'name': 'Delicious Candy Corn', 'description': 'Made in 1911', 'type': 'event'},
            76: {'name': 'Bat', 'description': 'I am vengence! I am the night!', 'type': 'event'},
            77: {'name': 'Jack', 'description': 'The Pumpkin King', 'type': 'event'},
            81: {'name': 'Bacon', 'description': 'Awarded for reaching 6°', 'type': 'degree'},
            82: {'name': 'Moon', 'description': 'Awarded for reaching 11°', 'type': 'degree'},
            83: {'name': 'Freezing', 'description': 'Awarded for reaching 32°', 'type': 'degree'},
            84: {'name': 'Dolphin', 'description': 'Awarded for reaching 42°', 'type': 'degree'},
            85: {'name': 'Alien', 'description': 'Awarded for reaching 51°', 'type': 'degree'},
            86: {'name': 'Road Sign', 'description': 'Awarded for reaching 66°', 'type': 'degree'},
            87: {'name': 'Peace', 'description': 'Awarded for reaching 69°', 'type': 'degree'},
            88: {'name': 'Flux Capacitor', 'description': 'Awarded for reaching 88°', 'type': 'degree'},
            89: {'name': 'Microphone', 'description': 'Awarded for reaching 98°', 'type': 'degree'},
            90: {'name': 'Boiling', 'description': 'Awarded for reaching 100°', 'type': 'degree'},
            91: {'name': 'Boiling 2', 'description': 'Awarded for reaching 212°', 'type': 'degree'},
            97: {'name': 'Dalmatians', 'description': 'Awarded for reaching 101°', 'type': 'degree'},
            98: {'name': 'ABC', 'description': 'Awarded for reaching 123°', 'type': 'degree'},
            99: {'name': 'Love', 'description': 'Awarded for reaching 143°', 'type': 'degree'},
            100: {'name': 'Pokemon', 'description': 'Awarded for reaching 151°', 'type': 'degree'},
            101: {'name': 'Phi', 'description': 'Awarded for reaching 162°', 'type': 'degree'},
            102: {'name': 'U Turn', 'description': 'Awarded for reaching 180°', 'type': 'degree'},
            103: {'name': 'World', 'description': 'Awarded for reaching 196°', 'type': 'degree'},
            104: {'name': 'Penguin', 'description': 'Awarded for reaching 17°', 'type': 'degree'},
            105: {'name': 'Magma', 'description': 'Awarded for reaching 79°', 'type': 'degree'},
            106: {'name': 'Plane', 'description': 'Awarded for reaching 130°', 'type': 'degree'},
            107: {'name': 'Uranium', 'description': 'Awarded for reaching 238°', 'type': 'degree'},
            113: {'name': 'Bowling', 'description': 'Awarded for reaching 300°', 'type': 'degree'},
            114: {'name': 'Pi', 'description': 'Awarded for reaching 314°', 'type': 'degree'},
            115: {'name': 'Boxing', 'description': 'Awarded for reaching 276°', 'type': 'degree'},
            116: {'name': 'Pencil', 'description': 'Awarded for reaching 2°', 'type': 'degree'},
            117: {'name': 'Baseball', 'description': 'Awarded for reaching 9°', 'type': 'degree'},
            118: {'name': 'Tomato', 'description': 'Awarded for reaching 57°', 'type': 'degree'},
            119: {'name': 'Yellow Lightning', 'description': 'Awarded for reaching 110°', 'type': 'degree'},
            120: {'name': 'Blue Lightning', 'description': 'Awarded for reaching 220°', 'type': 'degree'},
            121: {'name': 'Bones', 'description': 'Awarded for reaching 206°', 'type': 'degree'},
            122: {'name': 'Arc Reactor', 'description': 'Awarded for reaching 360°', 'type': 'degree'},
            129: {'name': 'Happy 5th Birthday TagPro', 'description': 'Awarded for TagPro\'s 5th Birthday', 'type': 'event'},
            130: {'name': 'Coin', 'description': 'Awarded for good team work.', 'type': 'event'},
            131: {'name': 'Question Block', 'description': 'Awarded for incredible team work!', 'type': 'event'},
            }
    
    def __init__(self, player, match=None):
        super().__init__(b64decode(player['events']))
        
        self.__player = player
        self.__match = match
        self.__events = player['events']
        
        self._auth = player['auth']
        self._degree = player['degree']
        self._flair = player['flair']
        self._name = player['name']
        self._points = player['points']
        self._score = player['score']
        self._team = player['team']
    
    def auth(self): return self._auth
    def degree(self): return self._degree
    def name(self): return self._name
    def points(self): return self._points
    def score(self): return self._score
    def team(self): return self._team
    
    def flair(self): return self.FLAIR[self._flair] if self._flair in self.FLAIR else self.FLAIR[-1]
    
    def scoreboard(self):
        
        if hasattr(self, "_PlayerReader__scoreboard"): return self._PlayerReader__scoreboard
        
        scoreboard = self.__scoreboard = {
                'grabs':    0,
                'hold':     0,
                'captures': 0,
                'kisses':   0,
                'drops':    0,
                'pops':     0,
                'prevent':  0,
                'button':   0,
                'have':     0,
                'chase':    0,
                'takeovers':0,
                'combos':   0,
                'returns':  0,
                'tags':     0,
                'block':    0,
                'support':  0,
                'powerups': 0,
                'jj':       0,
                'rb':       0,
                'tp':       0,
                'ts':       0,
                'up':       0,
                'jj-time':  0,
                'rb-time':  0,
                'tp-time':  0,
                'ts-time':  0,
                'up-time':  0,
                'play':     0,
                'win':      None,
                'score':    self._score,
                'points':   self._points,
                }
        
        lastTimes = {
                'return': -1,
                'tag': -1}
        
        # Grabs / Hold time / Drops / Caps / Takeovers / Kisses:
        def grabEvent(time, newFlag, powers, newTeam):
            scoreboard['grabs'] += 1
            scoreboard["hold"] -= time
            if time == lastTimes['return']: scoreboard['takeovers'] += 1
            # TODO: handle the edge case!! Grabbing while returning!
        self._grabEvent = grabEvent
        
        def dropEvent(time, oldFlag, powers, team):
            scoreboard["drops"] += 1
            scoreboard['pops'] += 1
            scoreboard["hold"] += time
            if time == lastTimes['return']: scoreboard['kisses'] += 1
            # TODO: handle the edge case! (returning via gate, while getting tagged)
        self._dropEvent = dropEvent
        
        def captureEvent(time, oldFlag, powers, team):
            scoreboard['captures'] += 1
            scoreboard['hold'] += time
        self._captureEvent = captureEvent
        
        def flagglessCaptureEvent(time, flag, powers, team):
            scoreboard["captures"] += 1
        self._flagglessCaptureEvent = flagglessCaptureEvent
        
        # Pops:
        def popEvent(time, powers, team):
            scoreboard["pops"] += 1
        self._popEvent = popEvent
        
        # Prevent time:
        def startPreventEvent(time, flag, powers, team):
            scoreboard["prevent"] -= time
        self._startPreventEvent = startPreventEvent
        
        def stopPreventEvent(time, flag, powers, team):
            scoreboard['prevent'] += time
        self._stopPreventEvent = stopPreventEvent
        
        # TODO: Have time
        scoreboard['have'] = None
        
        # Button time:
        def startButtonEvent(time, flag, powers, team):
            scoreboard["button"] -= time
        self._startButtonEvent = startButtonEvent
        
        def stopButtonEvent(time, flag, powers, team):
            scoreboard['button'] += time
        self._stopButtonEvent = stopButtonEvent
        
        # Block Time:
        def startBlockEvent(time, flag, powers, team):
            scoreboard["block"] -= time
        self._startBlockEvent = startBlockEvent
        
        def stopBlockEvent(time, flag, powers, team):
            scoreboard['block'] += time
        self._stopBlockEvent = stopBlockEvent
        
        # Tags and Combos:
        def tagEvent(time, flag, powers, team):
            scoreboard['tags'] += 1
            if time == lastTimes['tag']: scoreboard['combos'] += 1
            lastTimes['tag'] = time
        self._tagEvent = tagEvent
        
        # Returns:
        def returnEvent(time, flag, powers, team):
            scoreboard['returns'] += 1
            scoreboard['tags'] += 1
            lastTimes['return'] = time
        self._returnEvent = returnEvent
        
        # TODO: Chase time
        scoreboard['chase'] = None
        
        # Powerups:
        def powerupEvent(time, flag, powerUp, newPowers, team):
            scoreboard["powerups"] += 1
            pup = "jj" if powerUp==1 else "rb" if powerUp==2 else "tp" if powerUp==4 else "ts" if powerUp==8 else "up"
            scoreboard[pup] += 1
            scoreboard[pup+"-time"] -= time
        self._powerupEvent = powerupEvent
        
        def duplicatePowerupEvent(time, flag, powers, team):
            scoreboard["powerups"] += 1
        self._duplicatePowerupEvent = duplicatePowerupEvent
        
        def powerdownEvent(time, flag, powerDown, newPowers, team):
            pup = "jj" if powerDown==1 else "rb" if powerDown==2 else "tp" if powerDown==4 else "ts" if powerDown==8 else "up"
            scoreboard[pup+"-time"] += time
        self._powerdownEvent = powerdownEvent
            
        # Play time:
        def joinEvent(time, newTeam):
            scoreboard["play"] -= time
        self._joinEvent = joinEvent
        def quitEvent(time, oldFlag, oldPowers, oldTeam):
            scoreboard["play"] += time
        self._quitEvent = quitEvent
        
        # End hold/pup timers on switch/end:
        def switchEvent(time, oldFlag, oldPowers, oldTeam):
            if oldFlag: scoreboard["hold"] += time
        self._switchEvent = switchEvent
        
        def endEvent(time, flag, powers, team):
            if self._PlayerReader__match:
                scoreboard['play'] += time
                if flag: scoreboard["hold"] += time
                if powers & self.JUKE_JUICE_POWER: scoreboard["jj-time"] += time
                if powers & self.ROLLING_BOMB_POWER: scoreboard["rb-time"] += time
                if powers & self.TAG_PRO_POWER: scoreboard["tp-time"] += time
                if powers & self.TOP_SPEED_POWER: scoreboard["ts-time"] += time
            else:
                scoreboard['play'] = None
                if flag: scoreboard["hold"] = None
                if powers & self.JUKE_JUICE_POWER: scoreboard["jj-time"] = None
                if powers & self.ROLLING_BOMB_POWER: scoreboard["rb-time"] = None
                if powers & self.TAG_PRO_POWER: scoreboard["tp-time"] = None
                if powers & self.TOP_SPEED_POWER: scoreboard["ts-time"] = None
            
            # Win
            scoreboard['win'] = self._PlayerReader__match['teams'][team - 1]['score'] \
                - self._PlayerReader__match['teams'][team - 2]['score'] > 0 if \
                self._PlayerReader__match else None
        self._endEvent = endEvent
        
        self.read()
        
        # Support time:
        scoreboard['support'] = scoreboard['block'] + scoreboard['button']
        
        return scoreboard
    
    def captures(self):
        
        captures = []
        
        self._captureEvent = lambda time, oldFlag, powers, team: \
                captures.append(
                        {'time':time,
                         'oldFlag':oldFlag,
                         'powers':powers,
                         'team':team,
                         'player':self._name})
                
        return captures
    
    def timeline(self):
        
        def joinEvent(time, newTeam):
            team_name = self._PlayerReader__match['teams'][newTeam-1]['name'] \
                if self._PlayerReader__match else 'Red' if newTeam == 1 \
                else 'Blue' if newTeam == 2 else '??'
            print(timeFormat(time, True), self._name, 'joins '+team_name, sep="\t")
        self._joinEvent = joinEvent
        
        def quitEvent(time, oldFlag, oldPowers, oldTeam):
            team_name = self._PlayerReader__match['teams'][oldTeam-1]['name'] \
                if self._PlayerReader__match else 'Red' if oldTeam == 1 \
                else 'Blue' if oldTeam == 2 else '??'
            print(timeFormat(time, True), self._name, 'quits '+team_name, sep="\t")
        self._quitEvent = quitEvent
        
        def switchEvent(time, oldFlag, powers, newTeam):
            team_name = self._PlayerReader__match['teams'][newTeam-1]['name'] \
                if self._PlayerReader__match else 'Red' if newTeam == 1 \
                else 'Blue' if newTeam == 2 else '??'
            print(timeFormat(time, True), self._name, 'switches to '+team_name, sep="\t")
        self._switchEvent = switchEvent
        
        def grabEvent(time, newFlag, powers, team):
            print(timeFormat(time, True), self._name, 'grabs', sep="\t")
        self._grabEvent = grabEvent
        
        def captureEvent(time, oldFlag, powers, team):
            print(timeFormat(time, True), self._name, 'captures the flag', sep="\t")
        self._captureEvent = captureEvent
        
        def flaglessCaptureEvent(time, flag, powers, team):
            print(timeFormat(time, True), self._name, 'captures the marsball', sep="\t")
        self._flagglessCaptureEvent = flaglessCaptureEvent
        
        def powerupEvent(time, flag, powerUp, newPowers, team):
            powerup = 'Juke Juice' if powerUp == 1 else \
                'Rolling Bomb' if powerUp == 2 else \
                'Tag Pro' if powerUp == 4 else \
                'Top Speed' if powerUp == 8 else \
                'Unknown Powerup'
            print(timeFormat(time, True), self._name, 'gets a '+powerup, sep="\t")
        self._powerupEvent = powerupEvent
        
        def duplicatePowerupEvent(time, flag, powers, team):
            print(timeFormat(time, True), self._name, 'gets a duplicate powerup', sep="\t")
        self._duplicatePowerupEvent = duplicatePowerupEvent
        
        def powerdownEvent(time, flag, powerDown, newPowers, team):
            powerup = 'Juke Juice' if powerUp == 1 else \
                'Rolling Bomb' if powerUp == 2 else \
                'Tag Pro' if powerUp == 4 else \
                'Top Speed' if powerUp == 8 else \
                'Unknown Powerup'
            print(timeFormat(time, True), self._name, powerup+' runs out', sep="\t")
        self._powerdownEvent = powerdownEvent
        
        def returnEvent(time, flag, powers, team):
            print(timeFormat(time, True), self._name, 'returns', sep="\t")
        self._returnEvent = returnEvent
        
        def tagEvent(time, flag, powers, team):
            print(timeFormat(time, True), self._name, 'tags', sep="\t")
        self._tagEvent = tagEvent
        
        def dropEvent(time, oldFlag, powers, team):
            print(timeFormat(time, True), self._name, 'drops the flag', sep="\t")
        self._dropEvent = dropEvent
        
        def popEvent(time, powers, team):
            print(timeFormat(time, True), self._name, 'pops', sep="\t")
        self._popEvent = popEvent
        
        def startPreventEvent(time, flag, powers, team):
            print(timeFormat(time, True), self._name, 'starts preventing', sep="\t")
        self._startPreventEvent = startPreventEvent
        
        def stopPreventEvent(time, flag, powers, team):
            print(timeFormat(time, True), self._name, 'stops preventing', sep="\t")
        self._stopPreventEvent = stopPreventEvent
        
        def startButtonEvent(time, flag, powers, team):
            print(timeFormat(time, True), self._name, 'starts buttoning', sep="\t")
        self._startButtonEvent = startButtonEvent
        
        def stopButtonEvent(time, flag, powers, team):
            print(timeFormat(time, True), self._name, 'stops buttoning', sep="\t")
        self._stopButtonEvent = stopButtonEvent
        
        def startBlockEvent(time, flag, powers, team):
            print(timeFormat(time, True), self._name, 'starts blocking', sep="\t")
        self._startBlockEvent = startBlockEvent
        
        def stopBlockEvent(time, flag, powers, team):
            print(timeFormat(time, True), self._name, 'stops blocking', sep="\t")
        self._stopBlockEvent = stopBlockEvent
        
        def endEvent(time, flag, powers, team):
            win = self._PlayerReader__match['teams'][team - 1]['score'] \
                - self._PlayerReader__match['teams'][team - 2]['score'] > 0 if \
                self._PlayerReader__match else None
            print(timeFormat(time, True), self._name, 'wins' if win==1 else 'looses' if win==0 else 'ends', sep="\t")
        self._endEvent = endEvent
        
        self.read()
    
    def read(self):
        self._LogReader__pos = 0
        team = self._team
        time = 0
        flag = self.NO_FLAG
        powers = self.NO_POWER
        prevent = 0
        button = False
        block = False
        while not self._end():
            if not self._readBool(): newTeam = team
            elif not team: newTeam = 1 + self._readBool()
            elif not self._readBool(): newTeam = 3 - team
            else: newTeam = self.NO_TEAM
            dropPop = self._readBool()
            returns = self._readTally()
            tags = self._readTally()
            grab = not flag and self._readBool()
            captures = self._readTally()
            keep = not dropPop and newTeam and (newTeam == team or not team) \
            and (not captures or (not flag and not grab) or self._readBool())
            if not grab: newFlag = flag
            elif not keep: newFlag = self.TEMPORARY_FLAG
            else: newFlag = self._readFixed(2) + 1
            powerups = self._readTally()
            powersDown = self.NO_POWER
            powersUp = self.NO_POWER
            for i in [1,2,4,8]:
                if powers & i:
                    if self._readBool(): powersDown |= i
                elif powerups and self._readBool():
                    powersUp |= i
                    powerups -= 1
            togglePrevent = self._readBool()
            toggleButton = self._readBool()
            toggleBlock = self._readBool()
            time += 1 + self._readFooter()
            if(not team and newTeam):
                team = newTeam
                self._joinEvent(time, team)
            for _ in range(returns): self._returnEvent(time, flag, powers, team)
            for _ in range(tags): self._tagEvent(time, flag, powers, team)
            if grab:
                flag = newFlag
                self._grabEvent(time, flag, powers, team)
            for _ in range(captures):
                if keep or not flag: self._flaglessCaptureEvent(time, flag, powers, team)
                else:
                    self._captureEvent(time, flag, powers, team)
                    flag = self.NO_FLAG
                    keep = True
            for i in [1,2,4,8]:
                if powersDown & i:
                    powers ^= i
                    self._powerdownEvent(time, flag, i, powers, team)
                elif powersUp & i:
                    powers |= i
                    self._powerupEvent(time, flag, i, powers, team)
            for _ in range(powerups):
                self._duplicatePowerupEvent(time, flag, powers, team)
            if togglePrevent and prevent:
                self._stopPreventEvent(time, flag, powers, team)
                prevent = False
            elif togglePrevent:
                self._startPreventEvent(time, flag, powers, team)
                prevent = True
            if toggleButton and button:
                self._stopButtonEvent(time, flag, powers, team)
                button = False
            elif toggleButton:
                self._startButtonEvent(time, flag, powers, team)
                button = True
            if toggleBlock and block:
                self._stopBlockEvent(time, flag, powers, team)
                block = False
            elif toggleBlock:
                self._startBlockEvent(time, flag, powers, team)
                block = True
            if dropPop and flag:
                self._dropEvent(time, flag, powers, team)
                flag = self.NO_FLAG
            elif dropPop:
                self._popEvent(time, powers, team)
            if newTeam != team:
                if not newTeam:
                    self._quitEvent(time, flag, powers, team)
                    powers = self.NO_POWER
                else: self._switchEvent(time, flag, powers, newTeam)
                flag = self.NO_FLAG
                team = newTeam
        self._endEvent(self._PlayerReader__match['duration'] if \
                       self._PlayerReader__match else None, flag, powers, team)

class PlayerLogTimeline(PlayerReader):
    
    def _joinEvent(self, time, newTeam):
        l = locals()
        l.pop('self')
        print("join",l,sep='\t')
    def _quitEvent(self, time, oldFlag, oldPowers, oldTeam):
        l = locals()
        l.pop('self')
        print("quit",l,sep='\t')
    def _switchEvent(self, time, oldFlag, powers, newTeam):
        l = locals()
        l.pop('self')
        print("switch",l,sep='\t')
    def _grabEvent(self, time, newFlag, powers, team):
        l = locals()
        l.pop('self')
        print("grab",l,sep='\t')
    def _captureEvent(self, time, oldFlag, powers, team):
        l = locals()
        l.pop('self')
        print("capture",l,sep='\t')
    def _flaglessCaptureEvent(self, time, flag, powers, team):
        l = locals()
        l.pop('self')
        print("flaggless capture",l,sep='\t')
    def _powerupEvent(self, time, flag, powerUp, newPowers, team):
        l = locals()
        l.pop('self')
        print("powerup",l,sep='\t')
    def _duplicatePowerupEvent(self, time, flag, powers, team):
        l = locals()
        l.pop('self')
        print("duplicate powerup",l,sep='\t')
    def _powerdownEvent(self, time, flag, powerDown, newPowers, team):
        l = locals()
        l.pop('self')
        print("powerdown",l,sep='\t')
    def _returnEvent(self, time, flag, powers, team):
        l = locals()
        l.pop('self')
        print("return",l,sep='\t')
    def _tagEvent(self, time, flag, powers, team):
        l = locals()
        l.pop('self')
        print("tag",l,sep='\t')
    def _dropEvent(self, time, oldFlag, powers, team):
        l = locals()
        l.pop('self')
        print("drop",l,sep='\t')
    def _popEvent(self, time, powers, team):
        l = locals()
        l.pop('self')
        print("pop",l,sep='\t')
    def _startPreventEvent(self, time, flag, powers, team):
        l = locals()
        l.pop('self')
        print("start prevent",l,sep='\t')
    def _stopPreventEvent(self, time, flag, powers, team):
        l = locals()
        l.pop('self')
        print("stop prevent",l,sep='\t')
    def _startButtonEvent(self, time, flag, powers, team):
        l = locals()
        l.pop('self')
        print("start button",l,sep='\t')
    def _stopButtonEvent(self, time, flag, powers, team):
        l = locals()
        l.pop('self')
        print("stop button",l,sep='\t')
    def _startBlockEvent(self, time, flag, powers, team):
        l = locals()
        l.pop('self')
        print("start block",l,sep='\t')
    def _stopBlockEvent(self, time, flag, powers, team):
        l = locals()
        l.pop('self')
        print("stop block",l,sep='\t')
    def _endEvent(self, time, flag, powers, team):
        l = locals()
        l.pop('self')
        print("end",l,sep='\t')
    
    def __init__(self, player, match={}):
        print("Player:",player["name"])
        self.player = player
        self.match = match

        super().__init__(player, match)
        
        self.read()

class MatchReader():
    
    def __init__(self, match, matchId=0):
        
        self.__match = match
        self._matchId = matchId
        self._date = match['date']
        self._duration = match['duration']
        self._finished = match['finished']
        self._group = match['group']
        self._mapId = match['mapId']
        self._official = match['official']
        self._players = match['players']
        self._port = match['port']
        self._server = match['server']
        self._teams = match['teams']
        self._timeLimit = match['timeLimit']
    
    def score(self, team=0):
        
        if team == 0: return (self._teams[0]['score'], self._teams[1]['score'])
        if team in ['red','Red',1]: return self._teams[0]['score']
        if team in ['blue','Blue',2]: return self._teams[1]['score']
        for t in self._teams:
            if team == t['name']: return t['score']
        
        raise ValueError("'"+str(team)+"' is not a valid team name, color or number")
    
    def teamName(self, team=0):
        
        if team == 0: return (self._teams[0]['name'], self._teams[1]['name'])
        if team in ['red','Red',1]: return self._teams[0]['name']
        if team in ['blue','Blue',2]: return self._teams[1]['name']
        for t in self._teams:
            if team == t['name']: return t['name']
        
        raise ValueError("'"+str(team)+"' is not a valid team name, color or number")
    
    def summary(self):
        
        summary =  'Teams:\t'       + self.teamName()
        summary += '\nScore:\t'     + self.score()
        summary += '\nMap:\t'       + self._mapId
        summary += '\nDuration:\t'  + timeFormat(self._duration) \
                + (" (full-time)" if self._duration == 3600 * self._timeLimit \
                   else " ("+self._timeLimit+":00 time limit)")
        summary += '\nRed players:'
        
        print(summary)
        
    def captures(self, team=0):
        
        captures = []
        
        for player in self._players:

            PR = PlayerReader(player, self._MatchReader__match)
            PR._captureEvent = lambda time, oldFlag, powers, team: \
                captures.append(
                        {'time':time,
                         'oldFlag':oldFlag,
                         'powers':powers,
                         'team':team,
                         'player':player['name']})
            PR.read()
        
        captures.sort(key = lambda cap: cap['time'])
        
        return captures
        
        
        
# Helper funcitons

def printBits(blob):
    
    for i,byte in enumerate(b64decode(blob)):
        print(str(i)+':\t'+ ('0000000' + bin(byte)[2:])[-8:] )
    
    return 0

def timeFormat(time, decis=False):
    
    if decis: return "%d:%02d:%03d" % (int(time/3600), int(time%3600/60), round(time%60/.6))
    return "%d:%02d" % (int(time/3600), round(time%3600/60))
