import discord
from discord.ext import commands
import os
import json
import random
import datetime
from keep_alive import keep_alive

client = commands.Bot(command_prefix="!", intents=discord.Intents.all())


#Show that bot is connected
@client.event
async def on_ready():
    print("Bot is connected.")


#Command to show points/leaderboard
@client.command(aliases=["lb", "leaderboard"])
async def points(ctx, sort=None):
    with open("points.json", "r") as f:
        db = json.load(f)
    with open("mvpoints.json", "r") as f:
        mp = json.load(f)
    if sort == "--unsorted":
        embed = discord.Embed(
            title="SangSquad Bingo Leaderboard",
            description=
            f"Team Points:\n\nTeam 1: {db['team1']}\nTeam 2: {db['team2']}\nTeam 3: {db['team3']}\nTeam 4: {db['team4']}\nTeam 5: {db['team5']}\nTeam 6: {db['team6']}"
        )
        await ctx.send(embed=embed)
    else:
        sorted_teams = sorted(db.items(), key=lambda x: x[1], reverse=True)
        sorted_mp = sorted(mp.items(),
                           key=lambda x: x[1]["points"],
                           reverse=True)
        description = "Team Points:\n\n"
        for team, points in sorted_teams:
            description += f"{team}: {points}\n"
        description += "\nTop 5 Individual Points:\n\n"
        for _, mvp in sorted_mp[:5]:
            description += f"{mvp['Name']}: {mvp['points']}\n"
        embed = discord.Embed(title='SangSquad Bingo Leaderboard',
                              description=description,
                              timestamp=datetime.datetime.utcnow())
        await ctx.send(embed=embed)


#command to show individual points
@client.command()
async def mvp(ctx):
    with open("mvpoints.json", "r") as f:
        mp = json.load(f)
    sorted_mp = sorted(mp.items(), key=lambda x: x[1]["points"], reverse=True)
    description = "Individual Points:\n\n"
    for points, mvp in sorted_mp:
        description += f"{mvp['Name']}: {mvp['points']}\n"
    embed = discord.Embed(title="SangSquad Bingo MVP",
                          description=description,
                          timestamp=datetime.datetime.utcnow())
    await ctx.send(embed=embed)


#Command to add points to a team
@client.command()
@commands.has_permissions(administrator=True)
async def add(ctx, team: str, points_added: eval):
    with open("points.json", "r") as f:
        points = json.load(f)
    points[f"{team}"] += points_added
    with open("points.json", "w") as f:
        json.dump(points, f)
    await ctx.send(f"Added {points_added} points to {team}.")


#Command to add points to a team and individual
@client.command(aliases=["ap"])
@commands.has_permissions(administrator=True)
async def addpoints(ctx, team: str, points_added: eval,
                    member: discord.Member):
    with open("points.json", "r") as f:
        points = json.load(f)
    points[f"{team}"] += points_added
    with open("points.json", "w") as f:
        json.dump(points, f)
    with open("mvpoints.json", "r") as f:
        mp = json.load(f)
    member_id = str(member.id)
    if member_id not in mp:
        mp[member_id] = {}
        mp[member_id]["Name"] = member.name
        mp[member_id]["points"] = points_added
    else:
        mp[member_id]["points"] += points_added
    with open("mvpoints.json", "w") as f:
        json.dump(mp, f, indent=4)
    await ctx.send(f"Added {points_added} points to {team} and {member.name}.")


#Command to delete points from a team
@client.command(aliases=["del"])
@commands.has_permissions(administrator=True)
async def delete(ctx, team, points_del: eval):
    with open("points.json", "r") as f:
        points = json.load(f)
    points[f"{team}"] -= points_del
    with open("points.json", "w") as f:
        json.dump(points, f)
    await ctx.send(f"Removed {points_del} points from {team}.")


#Command to set points to a team
@client.command()
@commands.has_permissions(administrator=True)
async def set(ctx, team, points_set: int):
    with open("points.json", "r") as f:
        points = json.load(f)
    points[f"{team}"] = points_set
    with open("points.json", "w") as f:
        json.dump(points, f)
    await ctx.send(f"Set {team} to {points_set}")


# #Command to add individual points
@client.command(aliases=["ma"])
@commands.has_permissions(administrator=True)
async def mvpadd(ctx, member: discord.Member, points: eval):
    with open("mvpoints.json", "r") as f:
        mp = json.load(f)
    member_id = str(member.id)
    if member_id not in mp:
        mp[member_id] = {}
        mp[member_id]["Name"] = member.name
        mp[member_id]["points"] = points
        await ctx.send(f'Added {points} points to {member.name}')
    else:
        mp[member_id]["points"] += points
        await ctx.send(f'Added {points} points to {member.name}')
    with open("mvpoints.json", "w") as f:
        json.dump(mp, f, indent=4)


# #Command to delete individual points
@client.command(aliases=["md", "mvpdel"])
@commands.has_permissions(administrator=True)
async def mvpdelete(ctx, member: discord.Member, points: eval):
    with open("mvpoints.json", "r") as f:
        mp = json.load(f)
    member_id = str(member.id)
    mp[member_id]["points"] -= points
    with open("mvpoints.json", "w") as f:
        json.dump(mp, f, indent=4)
    await ctx.send(f'Removed {points} points to {member.name}')


#Command to set individual points
@client.command(aliases=["ms"])
@commands.has_permissions(administrator=True)
async def mvpset(ctx, member: discord.Member, points: eval):
    with open("mvpoints.json", "r") as f:
        mp = json.load(f)
        member_id = str(member.id)
        if member_id not in mp:
            mp[member_id] = {}
            mp[member_id]["Name"] = member.name
            mp[member_id]["points"] = points
            await ctx.send(f'{points} points set to {member.name}')
        else:
            mp[member_id]["points"] = points
            await ctx.send(f'{points} points set to {member.name}')
        with open("mvpoints.json", "w") as f:
            json.dump(mp, f, indent=4)


#Command to reset leaderboard
@client.command()
@commands.has_permissions(administrator=True)
async def reset(ctx, team=None):
    await ctx.send("Type `confirm` if you want to reset")

    def check(o):
        return o.content.lower() == "confirm" and str(o.author.id) == str(
            ctx.author.id)

    response = await client.wait_for('message', check=check, timeout=300.0)
    if "confirm" in response.content.lower():
        if team == None:
            with open("points.json", "r") as f:
                points = json.load(f)
            for i in points:
                points[i] = 0
            with open("points.json", "w") as f:
                json.dump(points, f)
            await ctx.send("Reset all points")
        else:
            with open("points.json", "r") as f:
                points = json.load(f)
            points[f"{team}"] = 0
            with open("points.json", "w") as f:
                json.dump(points, f)
            await ctx.send(f"Reset {team} to 0")


#Command to roll the dice
@client.command()
async def roll(ctx, team: str):
  #Open JSON files
  with open("tiles.json", "r") as f:
    tiles = json.load(f)
  with open("roll.json", "r") as f:
    rolls = json.load(f)
  with open("tilenames.json", "r") as f:
    tilesnames = json.load(f)
  with open("points.json", "r") as f:
      points = json.load(f)

  #Check if teams roll has been unlocked by admin if true
  if rolls[f"{team}"] is True:
    dice = random.randint(1, 3)
    description = f"{team} rolled a {dice}"
    tiles[f"{team}"] += dice
    if tiles[f"{team}"] == 8 or tiles[f"{team}"] == 24 or tiles[f"{team}"] == 40 or tiles[f"{team}"] == 48:
      tiles[f"{team}"] += 2
    if tiles[f"{team}"] == 9 or tiles[f"{team}"] == 25 or tiles[f"{team}"] == 41 or tiles[f"{team}"] == 49:
      tiles[f"{team}"] += 1
    if tiles[f"{team}"] > 49:
      tiles[f"{team}"] = 50
    description += f"\n\n\n{team} has landed on "
    for name, spot in tilesnames.items():
      if tiles[f"{team}"] == spot:
        description += f"{name}."
    rolls[f"{team}"] = False
    if tiles[f"{team}"] == 10:
      if points[f"{team}"] >= 4 and points[f"{team}"] <= 8:
        description += f"\n{team} has 3 Kraken Tents."
      elif points[f"{team}"] >= 9 and points[f"{team}"] <= 13:
        description += f"\n{team} has Dragon Limbs."
      elif points[f"{team}"] >= 14 and points[f"{team}"] <= 23:
        description += f"\n{team} has Any Obby Armour Piece."
    elif tiles[f"{team}"] == 26:
      if points[f"{team}"] >= 9 and points[f"{team}"] <= 17:
        description += f"\n{team} has Monkey Tail."
      elif points[f"{team}"] >= 18 and points[f"{team}"] <= 28:
        description += f"\n{team} has Dragon Chainbody."
      elif points[f"{team}"] >= 29 and points[f"{team}"] <= 46:
        description += f"\n{team} has Chaos Robe Bottom."
    if tiles[f"{team}"] == 42:
      if points[f"{team}"] >= 11 and points[f"{team}"] <= 18:
        description += f"\n{team} has DK Finish Log(aside from pet)."
      elif points[f"{team}"] >= 19 and points[f"{team}"] <= 31:
        description += f"\n{team} has Eleven Signet."
      elif points[f"{team}"] >= 32 and points[f"{team}"] <= 50:
        description += f"\n{team} has Gnome Scarf."
        
    with open("tiles.json", "w") as f:
        json.dump(tiles, f)
    with open("roll.json", "w") as f:
        json.dump(rolls, f)
    embed = discord.Embed(title="SangSquad Dice Roll", description=description)
    if dice == 1:
      embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1101579115833872394/1101580033534984263/dice1_transparent.png")
    elif dice == 2:
      embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1101579115833872394/1101582115457470514/dice2_transparent.png")
    elif dice == 3:
      embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1101579115833872394/1102072563116548176/dice3_transparent.png")
    await ctx.send(embed=embed)

  else:
      description = f"{team} has to wait until an Administrator confirms your submission."
      embed = discord.Embed(title="SangSquad Dice Roll", description=description)
      await ctx.send(embed=embed)


#Command for admin to verify submission
@client.command()
@commands.has_permissions(administrator=True)
async def verify(ctx, team: str):
    with open("roll.json", "r") as f:
        rolls = json.load(f)
        rolls[f"{team}"] = True
    with open("roll.json", "w") as f:
        json.dump(rolls, f)
    with open("points.json", "r") as f:
        points = json.load(f)
    with open("tilenames.json", "r") as f:
        tilenames = json.load(f)
    with open("tilepoints.json", "r") as f:
        tilepoints = json.load(f)
    with open("tiles.json", "r") as f:
        tiles = json.load(f)
    description = f"{team} has"
    current_tile = tiles[f"{team}"]
    for name, spot in tilenames.items():
        if current_tile == spot:
            if name in tilepoints:
                points[f"{team}"] += tilepoints[f"{name}"]
                description += f" {tilepoints[f'{name}']} points added to their score."
            break
    with open("points.json", "w") as f:
        json.dump(points, f)
    embed = discord.Embed(title="SangSquad Dice Roll", description=description)
    await ctx.send(embed=embed)


#Command to show what tile you are on
@client.command()
async def tile(ctx, team: str):
    with open("tiles.json", "r") as f:
      tiles = json.load(f)
    with open("tilenames.json", "r") as f:
      tilesnames = json.load(f)
    with open("points.json", "r") as f:
      points = json.load(f)
    description = f"{team} is on "
    for name, spot in tilesnames.items():
        if tiles[f"{team}"] == spot:
            description += f"{name}."
    if tiles[f"{team}"] == 10:
      if points[f"{team}"] >= 4 and points[f"{team}"] <= 8:
        description += f"\n{team} has 3 Kraken Tents."
      elif points[f"{team}"] >= 9 and points[f"{team}"] <= 13:
        description += f"\n{team} has Dragon Limbs."
      elif points[f"{team}"] >= 14 and points[f"{team}"] <= 23:
        description += f"\n{team} has Any Obby Armour Piece."
    elif tiles[f"{team}"] == 26:
      if points[f"{team}"] >= 9 and points[f"{team}"] <= 17:
        description += f"\n{team} has Monkey Tail."
      elif points[f"{team}"] >= 18 and points[f"{team}"] <= 28:
        description += f"\n{team} has Dragon Chainbody."
      elif points[f"{team}"] >= 29 and points[f"{team}"] <= 46:
        description += f"\n{team} has Chaos Robe Bottom."
    if tiles[f"{team}"] == 42:
      if points[f"{team}"] >= 11 and points[f"{team}"] <= 18:
        description += f"\n{team} has DK Finish Log(aside from pet)."
      elif points[f"{team}"] >= 19 and points[f"{team}"] <= 31:
        description += f"\n{team} has Eleven Signet."
      elif points[f"{team}"] >= 32 and points[f"{team}"] <= 50:
        description += f"\n{team} has Gnome Scarf."
    embed = discord.Embed(title="SangSquad Dice Roll", description=description)
    await ctx.send(embed=embed)


#Command for admin to unlock a reroll
@client.command()
@commands.has_permissions(administrator=True)
async def reroll(ctx, team: str):
    with open("roll.json", "r") as f:
        rolls = json.load(f)
        rolls[f"{team}"] = True
    with open("roll.json", "w") as f:
        json.dump(rolls, f)
    description = f"{team} has selected to reroll."
    embed = discord.Embed(title="SangSquad Dice Roll", description=description)
    await ctx.send(embed=embed)


keep_alive()

#Run bot
client.run(os.environ['TOKEN'])
