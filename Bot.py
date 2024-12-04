import datetime, requests, discord, roapipy, asyncio, json, os
from discord import app_commands
from discord.ext import commands, tasks
from discord.app_commands import Choice

client = commands.Bot(command_prefix = '!', intents=discord.Intents.all())
client.remove_command('help')
os.chdir("D:\RCSO\Bot")
tree = client.tree
roclient = roapipy.Client()

pointsdir = "points.json"
loadir = "loa.json"

recentlogs = []
rcsoranks = {'Guest': {'id': 43198238, 'rank': 0, 'holders': 0}, 'Suspended': {'id': 44374802, 'rank': 10, 'holders': 3}, 'Corrections Officer': {'id': 78480650, 'rank': 195, 'holders': 14}, 'Cadet': {'id': 44374786, 'rank': 200, 'holders': 0}, 'Probationary Deputy': {'id': 46479211, 'rank': 205, 'holders': 0}, 'Deputy': {'id': 44374750, 'rank': 210, 'holders': 31}, 'Deputy First Class': {'id': 46479777, 'rank': 215, 'holders': 16}, 'Corporal': {'id': 44374660, 'rank': 220, 'holders': 4}, 'Sergeant': {'id': 44374650, 'rank': 225, 'holders': 9}, 'Lieutenant': {'id': 44374616, 'rank': 230, 'holders': 6}, 'Captain': {'id': 44374609, 'rank': 235, 'holders': 3}, 'Undersheriff': {'id': 44374599, 'rank': 240, 'holders': 1}, 'Sheriff': {'id': 43198237, 'rank': 245, 'holders': 1}, 'Developer Oversight': {'id': 43198236, 'rank': 250, 'holders': 2}, 'Holder': {'id': 43198235, 'rank': 255, 'holders': 1}}

@tasks.loop(minutes=1)
async def grouplogs():
    currentlogs = requests.get("https://groups.roblox.com/v1/groups/6768144/audit-log", params={"sortOrder": "Asc", "limit": 10}).text["data"]
    logschannel = client.get_channel(1033503148674920488)
    for el in currentlogs:
        if el not in recentlogs:
            userpfp = roclient.User.Info(el["description"]["TargetName"])["avatar"]
            if el["actionType"] == "Accept Join Request":
                await logschannel.send(embed=discord.Embed(title="Hired", colour=0x3cf55e, description=f"**{el['description']['TargetName']}**\nHas been hired into the Ridgeway County Sheriff's Office").set_thumbnail(url=userpfp))
            elif el["actionType"] == "Change Rank":
                if rcsoranks[el["description"]["NewRoleSetName"]]["rank"] > rcsoranks[el["description"]["OldRoleSetName"]]["rank"]:
                    await logschannel.send(embed=discord.Embed(title="Promotion", colour=0x3cf55e, description=f"**{el['description']['TargetName']}**\nHas been promoted from `{el['description']['OldRoleSetName']}` to `{el['description']['NewRoleSetName']}`").set_thumbnail(url=userpfp))
                else:
                    await logschannel.send(embed=discord.Embed(title="Demotion", colour=0xf5953c, description=f"**{el['description']['TargetName']}**\nHas been demoted from `{el['description']['OldRoleSetName']}` to `{el['description']['NewRoleSetName']}`").set_thumbnail(url=userpfp))
            elif el["actionType"] == "Remove Member":
                await logschannel.send(embed=discord.Embed(title="Fired", colour=0xf53c3c, description=f"**{el['description']['TargetName']}**\nHas been fired from the Ridgeway County Sheriff's Office").set_thumbnail(url=userpfp))
    recentlogs = currentlogs

@tasks.loop(hours=1)
async def loacheck():
    loadict = {}
    loaover = []
    realmembers = []
    with open(loadir, "r+") as f:
        data = json.load(f)
        for el in data:
            loadict[el] = data[el]
    for el in loadict:
        if datetime.datetime.strptime(loadict[el], "%m/%d/%y") < datetime.datetime.now():
            loaover.append(el)
    for el in loaover:
        try:
            client.get_user(el)
            realmembers.append(el)
        except:
            pass
    with open(loadir, "r+") as f:
        data = json.load(f)
        for el in loaover:
            del data[el]
            f.seek(0)
            f.truncate()
            json.dump(data, f, indent=4)
    rcsoserver = client.get_guild(1012337244184526929)
    loarole = rcsoserver.get_role(1033097947325419600)
    logschannel = client.get_channel(1033503148674920488)
    embed = discord.Embed(
        title="Leave of Absence",
        colour=0x3c8cf5,
        description=""
    )
    for el in realmembers:
        person = rcsoserver.get_member(int(el))
        embed.description = f"**{person.nick}**\nIs no longer on a Leave of Absence"
        userpfp = roclient.User.Info(person.nick)["avatar"]
        embed.set_thumbnail(url=userpfp)
        await logschannel.send(embed=embed)
        try:
            await person.remove_roles(loarole)
        except:
            pass

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="RCSO Officers"))
    print(f'RCSO Automation now online with {round(client.latency * 1000)}ms ping.')
    await loacheck.start()
    recentlogs = requests.get("https://groups.roblox.com/v1/groups/6768144/audit-log", params={"sortOrder": "Asc", "limit": 10}).text["data"]
    await grouplogs.start()

log = app_commands.Group(name="log", description="Logging")
tree.add_command(log)

@log.command(name="patrol", description="Log your patrol")
@app_commands.check(lambda interaction : 1017416587202011166 in [el.id for el in interaction.user.roles])
async def patrol(interaction : discord.Interaction, starttime : str, startsc : str, endtime : str, endsc : str):
    nonint = False
    try:
        int(starttime)
    except:
        nonint = True
    if nonint == False:
        try:
            int(endtime)
        except:
            nonint = True
    if nonint == False:
        if len(starttime) == 4 or len(endtime) != 4:
            if int(starttime[3]) > 9 or int(endtime[3]) > 9 or int(starttime[2]) > 5 or int(endtime[2]) > 5 or int(starttime[1]) > 9 or int(endtime[1]) > 9 or int(starttime[0]) > 2 or int(endtime[0]) > 2:
                await interaction.response.send_message(embed=discord.Embed(title="Patrol Error", colour=0x684F3A, description="Ensure that the time you entered is possible"))
            elif int(starttime[0]) == 2 and int(starttime[1]) > 4 or int(endtime[0]) == 2 and int(endtime[1]) > 4:
                await interaction.response.send_message(embed=discord.Embed(title="Patrol Error", colour=0x684F3A, description="Ensure that the time you entered is possible"))
            else:
                if int(endtime) < int(starttime):
                    start = datetime.datetime.strptime(starttime, "%H%M")
                    end = datetime.datetime.strptime(endtime, "%H%M")
                    diff = (end - start) + datetime.timedelta(days=1)
                else:
                    start = datetime.datetime.strptime(starttime, "%H%M")
                    end = datetime.datetime.strptime(endtime, "%H%M")
                    diff = end - start
                diff = datetime.datetime.strptime(str(diff), "%H:%M:%S")
                patrolchannel = client.get_channel(1033063152537042965)
                userpfp = roclient.User.Info(interaction.user.nick)["avatar"]
                await patrolchannel.send(embed=discord.Embed(title=f"{interaction.user.nick}", colour=0x684F3A, description=f"**Start/End**\n{starttime} - {endtime}\n\n**Time**\n{diff.hour} Hour(s) {diff.minute} Minute(s)\n\n**Evidence**\n{startsc}\n{endsc}").set_thumbnail(url=userpfp))
                await interaction.response.send_message(embed=discord.Embed(title="Patrol", colour=0x684F3A, description="Your patrol log has been sent for reviewal."))
        else:
            await interaction.response.send_message(embed=discord.Embed(title="Patrol Error", colour=0x684F3A, description="Ensure you enter the start and end time in military form.\nE.g; 0900, 1200, 1900"))
    else:
        await interaction.response.send_message(embed=discord.Embed(title="Patrol Error", colour=0x684F3A, description="When entering your start and end times, ensure they're written in military form.\nE.g; 0700, 1200, 1900, etc.\nAvoid the following: 19:00, 07:00 PM, 7PM, etc."))

@patrol.error
async def patrolerror(interaction, error):
    if isinstance(error, discord.app_commands.errors.CheckFailure):
        await interaction.response.send_message(embed=discord.Embed(title="Command Error", colour=0x684F3A, description="You do not have permission to run that command."))
    else:
        raise error

@log.command(name="loa", description="Log your leave of absence")
@app_commands.check(lambda interaction : 1017416587202011166 in [el.id for el in interaction.user.roles])
async def loa(interaction : discord.Interaction, until : str, reason : str):
    already = False
    with open(loadir, "r+") as f:
        data = json.load(f)
        if str(interaction.user.id) in data:
            already = True
    if already == False:
        if len(until) == 8:
            if until[2] == "/" and until[5] == "/":
                if int(until[0] + until[1]) > 12 or int(until[3] + until[4]) > 31 or int(until[6] + until[7]) not in [22, 23]:
                    await interaction.response.send_message(embed=discord.Embed(title="LOA Error", colour=0x684F3A, description="Ensure that the date you entered exists."))
                elif datetime.datetime.strptime(until, "%m/%d/%y") < datetime.datetime.now():
                    await interaction.response.send_message(embed=discord.Embed(title="LOA Error", colour=0x684F3A, description="Ensure that the date you entered is not in the past."))
                else:
                    loarole = interaction.guild.get_role(1033097947325419600)
                    logschannel = client.get_channel(1033503148674920488)
                    await interaction.user.add_roles(loarole)
                    userpfp = roclient.User.Info(interaction.user.nick)["avatar"]
                    await logschannel.send(embed=discord.Embed(title="Leave of Absence", colour=0x3c8cf5, description=f"**{interaction.user.nick}**\nUntil `{until}`").set_thumbnail(url=userpfp))
                    await interaction.response.send_message(embed=discord.Embed(title="LOA", colour=0x684F3A, description="Your LOA has been submitted."))
                    with open(loadir, "r+") as f:
                        data = json.load(f)
                        data[interaction.user.id] = until
                        f.seek(0)
                        f.truncate()
                        json.dump(data, f, indent=4)
            else:
                await interaction.response.send_message(embed=discord.Embed(title="LOA Error", colour=0x684F3A, description="Ensure you're using the correct format when request LOA.\nMM/DD/YY"))
        else:
            await interaction.response.send_message(embed=discord.Embed(title="LOA Error", colour=0x684F3A, description="Ensure you're using the correct format when request LOA.\nMM/DD/YY"))
    else:
        await interaction.response.send_message(embed=discord.Embed(title="LOA Error", colour=0x684F3A, description="Seems like you've already submitted a LOA."))

@loa.error
async def loaerror(interaction, error):
    if isinstance(error, discord.app_commands.errors.CheckFailure):
        await interaction.response.send_message(embed=discord.Embed(title="Command Error", colour=0x684F3A, description="You do not have permission to run that command."))
    else:
        raise error

check = app_commands.Group(name="check", description="Checking")
tree.add_command(check)

@check.command(name="points", description="Check someone's points")
@app_commands.check(lambda interaction : 1033100508178690088 in [el.id for el in interaction.user.roles])
async def checkpoints(interaction : discord.Interaction, who : discord.Member):
    userpfp = roclient.User.Info(who.nick)["avatar"]
    with open(pointsdir, "r+") as f:
        data = json.load(f)
        if str(who.id) in data:
            await interaction.response.send_message(embed=discord.Embed(title=f"{who.nick}'s Points", colour=0x684F3A, description=f"{who.mention} has `{data[str(who.id)]}` point(s)").set_thumbnail(url=userpfp))
        else:
            if 1017416587202011166 in [el.id for el in who.roles]:
                data[who.id] = 0
                f.seek(0)
                f.truncate()
                json.dump(data, f, indent=4)
                await interaction.response.send_message(embed=discord.Embed(title=f"{who.nick}'s Points", colour=0x684F3A, description=f"{who.mention} has `{data[str(who.id)]}` point(s)").set_thumbnail(url=userpfp))
            else:
                await interaction.response.send_message(embed=discord.Embed(title="Points Error", colour=0x684F3A, description="We couldn't find that user\nAre they a member of the RCSO?").set_thumbnail(url=userpfp))

@checkpoints.error
async def checkpointserror(interaction, error):
    if isinstance(error, discord.app_commands.errors.CheckFailure):
        await interaction.response.send_message(embed=discord.Embed(title="Command Error", colour=0x684F3A, description="You do not have permission to run that command."))
    else:
        raise error

@check.command(name="loa", description="Check someone's loa")
@app_commands.check(lambda interaction : 1033100508178690088 in [el.id for el in interaction.user.roles])
async def checkloa(interaction : discord.Interaction, who : discord.Member):
    userpfp = roclient.User.Info(who.nick)["avatar"]
    with open(loadir, "r+") as f:
        data = json.load(f)
        if str(who.id) in data:
            await interaction.response.send_message(embed=discord.Embed(title=f"{who.nick}'s LOA", colour=0x684F3A, description=f"{who.mention} has a LOA Until {data[str(who.id)]}").set_thumbnail(url=userpfp))
        else:
            await interaction.response.send_message(embed=discord.Embed(title="LOA Error", colour=0x684F3A, description="We couldn't find that user/they don't have a LOA").set_thumbnail(url=userpfp))

@checkloa.error
async def checkloaerror(interaction, error):
    if isinstance(error, discord.app_commands.errors.CheckFailure):
        await interaction.response.send_message(embed=discord.Embed(title="Command Error", colour=0x684F3A, description="You do not have permission to run that command."))
    else:
        raise error

@tree.command(name="actionreq", description="Request an action to be done")
@app_commands.choices(rank=[Choice(name="Administration", value="1033194749420642316"), Choice(name="Leadership", value="1033195789373145159")])
@app_commands.check(lambda interaction : 1033100508178690088 in [el.id for el in interaction.user.roles])
async def actionreq(interaction : discord.Interaction, action : str, rank : Choice[str]):
    pingrole = interaction.guild.get_role(int(rank.value))
    actionchannel = client.get_channel(1033196209013276672)
    await actionchannel.send(f"{pingrole.mention}", embed=discord.Embed(title=f"{interaction.user.nick}", colour=0x684F3A, description=f"{action}"))
    await interaction.response.send_message(embed=discord.Embed(title="Action Request", colour=0x684F3A, description="Your requested action has been sent for reviewal."))

@actionreq.error
async def actionreqerror(interaction, error):
    if isinstance(error, discord.app_commands.errors.CheckFailure):
        await interaction.response.send_message(embed=discord.Embed(title="Command Error", colour=0x684F3A, description="You do not have permission to run that command."))
    else:
        raise error

points = app_commands.Group(name="points", description="Points")
tree.add_command(points)

@points.command(name="self", description="Check your points")
@app_commands.check(lambda interaction : 1017416587202011166 in [el.id for el in interaction.user.roles])
async def self(interaction : discord.Interaction):
    userpfp = roclient.User.Info(interaction.user.nick)["avatar"]
    with open(pointsdir, "r+") as f:
        data = json.load(f)
        if str(interaction.user.id) not in data:
            data[str(interaction.user.id)] = 0
            f.seek(0)
            f.truncate()
            json.dump(data, f, indent=4)
        await interaction.response.send_message(embed=discord.Embed(title=f"{interaction.user.nick}'s Points", colour=0x684F3A, description=f"You have `{data[str(interaction.user.id)]}` point(s)").set_thumbnail(url=userpfp))

@self.error
async def selferror(interaction, error):
    if isinstance(error, discord.app_commands.errors.CheckFailure):
        await interaction.response.send_message(embed=discord.Embed(title="Command Error", colour=0x684F3A, description="You do not have permission to run that command."))
    else:
        raise error

@points.command(name="add", description="Add to someone's points")
@app_commands.check(lambda interaction : 1033100508178690088 in [el.id for el in interaction.user.roles])
async def add(interaction : discord.Interaction, who : discord.Member, amount : int):
    error = False
    userpfp = roclient.User.Info(who.nick)["avatar"]
    with open(pointsdir, "r+") as f:
        data = json.load(f)
        if str(who.id) not in data:
            if 1017416587202011166 in [el.id for el in interaction.user.roles]:
                data[str(who.id)] = amount
                f.seek(0)
                f.truncate()
                json.dump(data, f, indent=4)
            else:
                error = True
        else:
            data[str(who.id)] = data[str(who.id)] + amount
            f.seek(0)
            f.truncate()
            json.dump(data, f, indent=4)
    if error == False:
        await interaction.response.send_message(embed=discord.Embed(title=f"{who.nick}'s Points", colour=0x684F3A, description=f"{who.mention} now has `{data[str(who.id)]}` point(s)").set_thumbnail(url=userpfp))
    else:
        await interaction.response.send_message(embed=discord.Embed(title="Points Error", colour=0x684F3A, description="We couldn't find that user\nAre they a member of the RCSO?").set_thumbnail(url=userpfp))

@add.error
async def adderror(interaction, error):
    if isinstance(error, discord.app_commands.errors.CheckFailure):
        await interaction.response.send_message(embed=discord.Embed(title="Command Error", colour=0x684F3A, description="You do not have permission to run that command."))
    else:
        raise error

@points.command(name="remove", description="Remove from someone's points")
@app_commands.check(lambda interaction : 1033100508178690088 in [el.id for el in interaction.user.roles])
async def remove(interaction : discord.Interaction, who : discord.Member, amount : int):
    userpfp = roclient.User.Info(who.nick)["avatar"]
    error, neg = False, False
    with open(pointsdir, "r+") as f:
        data = json.load(f)
        if str(who.id) not in data:
            if 1017416587202011166 in [el.id for el in interaction.user.roles]:
                data[str(who.id)] = 0
                f.seek(0)
                f.truncate()
                json.dump(data, f, indent=4)
                neg = True
            else:
                error = True
        else:
            if (data[str(who.id)] - amount) < 0:
                error = True
            else:
                data[str(who.id)] = data[str(who.id)] - amount
                f.seek(0)
                f.truncate()
                json.dump(data, f, indent=4)
    if error == False:
        if neg == False:
            await interaction.response.send_message(embed=discord.Embed(title=f"{who.nick}'s Points", colour=0x684F3A, description=f"{who.mention} now has `{data[str(who.id)]}` point(s)").set_thumbnail(url=userpfp))
        else:
            await interaction.response.send_message(embed=discord.Embed(title=f"Points Error", colour=0x684F3A, description="A user cannot have negative points").set_thumbnail(url=userpfp))
    else:
        await interaction.response.send_message(embed=discord.Embed(title="Points Error", colour=0x684F3A, description="We couldn't find that user\nAre they a member of the RCSO?").set_thumbnail(url=userpfp))

@remove.error
async def removeerror(interaction, error):
    if isinstance(error, discord.app_commands.errors.CheckFailure):
        await interaction.response.send_message(embed=discord.Embed(title="Command Error", colour=0x684F3A, description="You do not have permission to run that command."))
    else:
        raise error

@points.command(name="set", description="Set someone's points")
@app_commands.check(lambda interaction : 1033100508178690088 in [el.id for el in interaction.user.roles])
async def setpoints(interaction : discord.Interaction, who : discord.Member, amount : int):
    if amount > 0:
        userpfp = roclient.User.Info(who.nick)["avatar"]
        error = False
        with open(pointsdir, "r+") as f:
            data = json.load(f)
            if str(who.id) in data:
                data[str(who.id)] = amount
                f.seek(0)
                f.truncate()
                json.dump(data, f, indent=4)
            else:
                if 1017416587202011166 in [el.id for el in interaction.user.roles]:
                    data[str(who.id)] = amount
                    f.seek(0)
                    f.truncate()
                    json.dump(data, f, indent=4)
                else:
                    error = True
        if error == False:
            await interaction.response.send_message(embed=discord.Embed(title=f"{who.nick}'s Points", colour=0x684F3A, description=f"{who.mention} now has `{data[str(who.id)]}` point(s)").set_thumbnail(url=userpfp))
        else:
            await interaction.response.send_message(embed=discord.Embed(title="Points Error", colour=0x684F3A, description="We couldn't find that user\nAre they a member of the RCSO?").set_thumbnail(url=userpfp))
    else:
        await interaction.response.send_message(embed=discord.Embed(title=f"Points Error", colour=0x684F3A, description="A user cannot have negative points").set_thumbnail(url=userpfp))

@setpoints.error
async def setpointserror(interaction, error):
    if isinstance(error, discord.app_commands.errors.CheckFailure):
        await interaction.response.send_message(embed=discord.Embed(title="Command Error", colour=0x684F3A, description="You do not have permission to run that command."))
    else:
        raise error

@client.command()
@commands.check(lambda ctx : ctx.author.id == 301014178703998987)
async def connect(ctx):
    await tree.sync()

client.run('MTAzMzA1NDE0MjkyODgwMTg4NA.Gdws3E.1g5BFX8_Tm4abNepOyfsCNWVzMsbDOJlHdjMRY')

#https://discord.com/api/oauth2/authorize?client_id=1033054142928801884&permissions=8&scope=bot

#General Hex (Brown) - 0x684F3A
#Hired/Promoted - 0x3cf55e
#Demoted - 0xf5953c
#Termination - 0xf53c3c
#Warning - 0xf5e63c
#LOA - 0x3c8cf5

"""
f.seek(0)
f.truncate()
json.dump(data, f, indent=4)
"""