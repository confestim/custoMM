from configparser import ConfigParser

class Config:
    def __init__(self) -> None:    
      config = ConfigParser()
      config.read("config.ini")
      self.URL = config["DEFAULT"]["URL"]
      self.team_1 = int(config['DISCORD']['TEAM_1'])
      self.team_2 = int(config['DISCORD']['TEAM_2'])
      self.token = config['DISCORD']['TOKEN']
      self.guild = int(config['DISCORD']['GUILD_ID'])
