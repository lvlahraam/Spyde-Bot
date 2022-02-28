import discord, random
from discord.ext import commands

class OnGuild(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild:discord.Guild):
        channel = random.choice(guild.text_channels)
        ogjmbed = discord.Embed(
            title="Thanks for inviting me!",
            description=F"\nHey there! Thanks for inviting me!\nIf you need any help, just type **{self.bot.default_prefix}help**",

        )
        await channel.send(embed=ogjmbed)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild:discord.Guild):
        del self.bot.prefixes[guild.id]
        await self.bot.mongodb.prefixes.find_one_and_delete({"guild_id": guild.id})
        await self.bot.mongodb.tickets.find_one_and_delete({"guild_id": guild.id})
        await self.bot.mongodb.welcome.find_one_and_delete({"guild_id": guild.id})
        await self.bot.mongodb.goodbye.find_one_and_delete({"guild_id": guild.id})

def setup(bot):
    bot.add_cog(OnGuild(bot))
