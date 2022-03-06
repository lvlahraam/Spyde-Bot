import discord, logging, motor.motor_asyncio, os, aiohttp, openrobot.api_wrapper
from core.views import help
from discord.ext import commands

logger = logging.getLogger("discord")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
handler.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s"))
logger.addHandler(handler)

async def create_client_mongodb():
    url = os.getenv("MONGODB_URL")
    bot.mongoclient = motor.motor_asyncio.AsyncIOMotorClient(url, serverSelectionTimeoutMS=5000)
    try:
        print("Created a MongoDB Client", await bot.mongoclient.server_info())
        bot.mongodb = bot.mongoclient.bot
    except Exception:
        print("Unable to connect to the server.")

async def get_prefix(bot, message:discord.Message):
    if not message.guild:
        return commands.when_mentioned_or(bot.default_prefix)(bot, message)
    prefix = bot.prefixes.get(message.guild.id)
    if not prefix:
        mongo = await bot.mongodb.prefixes.find_one({"guild_id": message.guild.id})
        if mongo:
            prefix = bot.prefixes[message.guild.id] = mongo["prefix"]
        else:
            prefix = bot.prefixes[message.guild.id] = bot.default_prefix
        print(F"Cached {prefix}{'/d' if not mongo else '/m'} | {message.guild.name} - {message.guild.id}")
    return commands.when_mentioned_or(prefix)(bot, message)

async def create_session_aiohttp():
    bot.session = aiohttp.ClientSession()
    print("Created a AioHttp Session")

# async def create_node_pomice():
#     await bot.wait_until_ready()
#     bot.pomice = pomice.NodePool()
#     spotify_id = os.getenv("SPOTIFY_ID")
#     spotify_secret = os.getenv("SPOTIFY_SECRET")
#     await bot.pomice.create_node(bot=bot, host="usa.lavalink.mitask.tech", port="2333", password="lvserver", identifier="US Lavalink", spotify_client_id=spotify_id, spotify_client_secret=spotify_secret)
#     print("Created a Pomice Node(s)")

class SpydeBase(commands.AutoShardedBot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tree = discord.app_commands.CommandTree(self)
        self.prefixes = {}
        self.default_prefix = ",s"
        self.color = 0x2C333A
        self.persistent_views_added = False
        self.afks = {}
        self._commands = []
        for command in sorted(os.listdir("./core/commands/")):
            if command.endswith(".py"):
                self.load_extension(F"core.commands.{command[:-3]}")
                self._commands.append(command[:-3])
        self._events = []
        for event in sorted(os.listdir("./core/events/")):
            if event.endswith(".py"):
                self.load_extension(F"core.events.{event[:-3]}")
                self._events.append(event[:-3])
        self._others = ["Jishaku"]
        self.load_extension("jishaku")
        os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
        os.environ["JISHAKU_NO_DM_TRACEBACK"] = "True"
        os.environ["GIT_DISCOVERY_ACROSS_FILESYSTEM"] = "True"
        self.get_command("jsk").hidden = True

    async def close(self):
        if not self.session.closed:
            await self.session.close()
        await super().close()

    def trim(self, text: str, limit: int):
        text = text.strip()
        if len(text) > limit: return text[:limit-3] + "..."
        return text

bot = SpydeBase(
    slash_commands=True,
    command_prefix=get_prefix,
    strip_after_prefix=True,
    case_insensitive=True,
    help_command=help.CustomHelp(),
    intents=discord.Intents.all(),
    allowed_mentions=discord.AllowedMentions(everyone=False, users=False, roles=False, replied_user=True)
)

@bot.check
async def blacklisted(ctx:commands.Context):
    reason = await bot.mongodb.blacklist.find_one({"user_id": ctx.author.id})
    if not reason: return True
    raise commands.CheckFailure(message=F"You are blacklisted: {reason['reason']}")

bot.openrobot = openrobot.api_wrapper.AsyncClient(token=os.getenv("OPENROBOT"))

bot.loop.run_until_complete(create_client_mongodb())
bot.loop.create_task(create_session_aiohttp())
# bot.loop.create_task(create_node_pomice())
bot.run(os.getenv("TOKEN"))
