import discord, logging, aiohttp, motor.motor_asyncio, os
from discord.ext import commands, tasks
from core.views import help

logger = logging.getLogger("discord")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
handler.setFormatter(
    logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
)
logger.addHandler(handler)


async def create_aiohttp_session():
    bot.session = aiohttp.ClientSession()
    print("Created a AioHttp Session")


async def create_mongodb_client():
    url = os.getenv("MONGODB")
    bot.mongoclient = motor.motor_asyncio.AsyncIOMotorClient(
        os.getenv("MONGODBURL"),
        serverSelectionTimeoutMS=5000,
    )
    try:
        print("Created a MongoDB Client", await bot.mongoclient.server_info())
        bot.mongodb = bot.mongoclient.bot
    except Exception:
        print("Unable to connect to the server.")


async def get_prefix(bot, message: discord.Message):
    if not message.guild:
        return commands.when_mentioned_or(bot.default_prefix)(bot, message)
    prefix = bot.prefixes.get(message.guild.id)
    if not prefix:
        mongo = await bot.mongodb.prefixes.find_one({"guild_id": message.guild.id})
        if mongo:
            prefix = bot.prefixes[message.guild.id] = mongo["prefix"]
        else:
            prefix = bot.prefixes[message.guild.id] = bot.default_prefix
        print(
            f"Cached {prefix}{'/d' if not mongo else '/m'} | {message.guild.name} - {message.guild.id}"
        )
    return commands.when_mentioned_or(prefix)(bot, message)


class SpydeBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=get_prefix,
            strip_after_prefix=True,
            intents=discord.Intents.all(),
            help_command=help.CustomHelp(),
        )
        self.default_prefix = ".s"
        self.prefixes = {}
        self.afks = {}
        self.color = 0x2F3136
        self._commands = []
        self._events = []
        self._others = []

    async def setup_hook(self):
        await create_aiohttp_session()
        await create_mongodb_client()
        for command in os.listdir("./core/commands/"):
            if command.endswith(".py"):
                await self.load_extension(f"core.commands.{command[:-3]}")
                self._commands.append(command)
        for event in os.listdir("./core/events/"):
            if event.endswith(".py"):
                await self.load_extension(f"core.events.{event[:-3]}")
                self._events.append(event)
        self.load_extension('jishaku')

    async def close(self):
        await self.session.close()
        await super().close()

    def embed(
        self,
        author: discord.User,
        title: str = None,
        description: str = None,
        fields: dict = None,
        footerText: str = None,
        footerUrl: str = None,
    ):
        embed = discord.Embed(
            color=self.color,
            title=title or "",
            description=description or "",
            timestamp=discord.utils.utcnow(),
        )
        embed.set_author(name=author.name, icon_url=author.display_avatar.url)
        if footerText:
            embed.set_footer(text=footerText, icon_url=footerUrl if footerUrl else "")
        if fields:
            for name, value in fields.items():
                embed.add_field(name=name, value=value)
        return embed


bot = SpydeBot()


@bot.check
async def blacklisted(ctx: commands.Context):
    reason = await bot.mongodb.blacklist.find_one({"user_id": ctx.author.id})
    if not reason:
        return True
    raise commands.CheckFailure(message=f"You are blacklisted: {reason['reason']}")


bot.run(token=os.getenv("TOKEN"))
