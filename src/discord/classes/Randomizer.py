from random import shuffle
from .Splitter import Splitter

class Randomizer(Splitter):
    def __init__(self, bot, author, ctx=None, interaction=None, slash=False):
        super().__init__(bot, author, ctx, interaction, slash)
    
   
    async def randomize(self):
            players = await self.ready()
            print(players)
            if not players:
                return False
            
            shuffle.shuffle(players)
            print([x.name for x in players[:int(len(players)/2)]], [x.name for x in players[int(len(players)/2):]])
            await self.split(players[:int(len(players)/2)], players[int(len(players)/2):])
            return True