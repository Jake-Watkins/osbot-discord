# osbot-discord

intended features:
  1. respond to $add itemname to add to users total loot
  2. this will lookup the items value using the osrs ge api and store this value along with a the screenshot to a googlesheets doc
  3. respond to $lookup user
  4. this will sum the total loot at the time of drop for this user


requires :
pip3 install discord.py gspread oath2client GitPython beautifulsoup4
