import discord
import constants

basicEmbeds = {
    "SelfNoProfile": discord.Embed(description="`You do not have a profile! Do /createprofile to begin!`", colour=constants.colorHexes["Danger"]),
    "OtherNoProfile": discord.Embed(description="`This user doesn't have a profile!`", colour=constants.colorHexes["Danger"]),
    "SelfNoPermission": discord.Embed(description="`You do not have permission to run this command!`", colour=constants.colorHexes["Danger"])
}