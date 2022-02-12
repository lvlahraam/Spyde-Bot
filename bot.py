import discord, logging, asyncpg, os, aiohttp, pomice, openrobot.api_wrapper, random
from core.views import help
from discord.ext import commands

logger = logging.getLogger("discord")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
handler.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s"))
logger.addHandler(handler)

async def create_pool_postgres():
    bot.postgres = await asyncpg.create_pool(dsn=os.getenv("DATABASE_URL"))
    print("Created to the Postgres Pool")
    tables = os.getenv("TABLES")
    if not tables:
        await bot.postgres.execute("CREATE TABLE IF NOT EXISTS blacklist (user_name text, user_id bigint, reason text)")
        await bot.postgres.execute("CREATE TABLE IF NOT EXISTS prefixes (guild_name text, guild_id bigint, prefix text)")
        await bot.postgres.execute("CREATE TABLE IF NOT EXISTS welcome (guild_name text, guild_id bigint, msg text, ch bigint)")
        await bot.postgres.execute("CREATE TABLE IF NOT EXISTS goodbye (guild_name text, guild_id bigint, msg text, ch bigint)")
        await bot.postgres.execute("CREATE TABLE IF NOT EXISTS tickets (guild_name text, guild_id bigint, cag bigint, num bigint)")
        await bot.postgres.execute("CREATE TABLE IF NOT EXISTS notes (user_name text, user_id bigint, task text, jump_url text)")
        os.environ["TABLES"] = "blacklist, prefixes, welcome, goodbye, tickets, notes"
    

async def get_prefix(bot, message:discord.Message):
    if not message.guild:
        return commands.when_mentioned_or(bot.default_prefix)(bot, message)
    prefix = bot.prefixes.get(message.guild.id)
    if prefix:
        return commands.when_mentioned_or(prefix)(bot, message)
    postgres = await bot.postgres.fetchval("SELECT prefix FROM prefixes WHERE guild_id=$1", message.guild.id)
    if postgres:
        prefix = bot.prefixes[message.guild.id] = postgres
    else:
        prefix = bot.prefixes[message.guild.id] = bot.default_prefix
    print(F"Cached {prefix}{'/d' if not postgres else '/p'} | {message.guild.name} - {message.guild.id}")
    return commands.when_mentioned_or(prefix)(bot, message)

async def create_session_aiohttp():
    bot.session = aiohttp.ClientSession()
    print("Created a AioHttp Session")

async def create_node_pomice():
    await bot.wait_until_ready()
    bot.pomice = pomice.NodePool()
    spotify_id = os.getenv("SPOTIFY_ID")
    spotify_secret = os.getenv("SPOTIFY_SECRET")
    await bot.pomice.create_node(bot=bot, host="lava.link", port="80", password="mom", identifier="node1lava.link", spotify_client_id=spotify_id, spotify_client_secret=spotify_secret)
    print("Created a Pomice Node(s)")

class SymBase(commands.AutoShardedBot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.prefixes = {}
        self.default_prefix = ",s"
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
        self.persistent_views_added = False

    async def close(self):
        if not self.session.closed:
            await self.session.close()
        await super().close()

    @property
    def color(self):
        colors = [0x2C333A, 0x5865F2, 0xF4E968]
        color = random.choice(colors)
        return color

    def trim(self, text: str, limit: int):
        text = text.strip()
        if len(text) > limit: return text[:limit-3] + "..."
        return text

bot = SymBase(
    slash_commands=True,
    command_prefix=get_prefix,
    strip_after_prefix=True,
    case_insensitive=True,
    help_command=help.CustomHelp(),
    intents=discord.Intents(administrator=True),
    allowed_mentions=discord.AllowedMentions(everyone=False, users=False, roles=False, replied_user=True)
)

@bot.check
async def blacklisted(ctx:commands.Context):
    reason = await bot.postgres.fetchval("SELECT reason FROM blacklist WHERE user_id=$1", ctx.author.id)
    if not reason: return True
    raise commands.CheckFailure(message=F"You are blacklisted: {reason}")

bot.openrobot = openrobot.api_wrapper.AsyncClient(token=os.getenv("OPENROBOT"))

bot.loop.run_until_complete(create_pool_postgres())
bot.loop.create_task(create_session_aiohttp())
bot.loop.create_task(create_node_pomice())
bot.run(os.getenv("TOKEN"))
