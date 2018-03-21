"""
tagpro-analytics : read raw match data from TagPro Analytics (tagpro.eu)

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



The original license of the PHP code that this project is based on had the condition that its license should be retained.
Following is the license of the original PHP code by Jeroen van der Gun, hosted on [tagpro.eu](https://tagpro.eu/?science).
I don't know wheather a completely rewritten distribution counts as a 'redistribution of source code', but I included it anyway.



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
    
class PlayerLogReader(LogReader):
    
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
    
    def __init__(self, data, team, duration):
        super().__init__(data)
        time = 0
        flag = self.NO_FLAG
        powers = self.NO_POWER
        prevent = False
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
            keep = not dropPop and newTeam and (newTeam == team or not team) and (not captures or (not flag and not grab) or self._readBool())
            if not grab: newFlag = flag
            elif not keep: newFlag = self.TEMPORARY_FLAG
            else: newFlag = self._readFixed(2)
            powerups = self._readTally()
            powersDown = self.NO_POWER
            powersUp = self.NO_POWER
            for i in [1,2,4,8]:
                if powers & i and self._readBool(): powersDown |= i
                elif powerups and self._readBool(): powersUp |= i
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
        self._endEvent(duration, flag, powers, team)

class PlayerLogTimeline(PlayerLogReader):
    
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
    
    def __init__(self, auth, name, flair, degree, score, points, team, events, duration):
        super().__init__(b64decode(events), team, duration)
        self.auth = auth
        self.name = name
        self.flair = flair
        self.degree = degree
        self.score = score
        self.points = points
        self.team = team
        self.events = events
