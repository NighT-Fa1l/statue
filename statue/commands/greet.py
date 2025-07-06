import asyncio
from discord.ext import commands

SPECIAL_USER_ID = 1327634023706660886  # Replace with actual user ID

class Greet(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cooldowns = set()  # keep track of users currently cooling down

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return  # ignore bots

        if message.author.id == SPECIAL_USER_ID:
            if message.author.id in self.cooldowns:
                # Still cooling down, do nothing
                return

            # Not cooling down — send greeting
            #await message.channel.send("Greetings Mr. {message.author.id}")
            await message.channel.send(f"Greetings Mr. {message.author.mention}")


            # Add user to cooldown set
            self.cooldowns.add(message.author.id)

            # Wait 20 minutes then remove cooldown
            await asyncio.sleep(1200)
            self.cooldowns.remove(message.author.id)

async def setup(bot):
    await bot.add_cog(Greet(bot))
