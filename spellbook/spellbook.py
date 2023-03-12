import discord
from tabulate import tabulate

from redbot.core import Config
from redbot.core import commands
from redbot.core.utils.menus import menu, DEFAULT_CONTROLS
from redbot.core.utils.chat_formatting import pagify

from .utils import *


class Spellbook(commands.Cog):
    """A D&D 5e Cog for Wizards to manage their spellbooks"""

    def __init__(self, bot):
        self.bot = bot
        default_member = {
            "Characterpic": None,
            "Spell": []
        }
        default_guild = {
            "db": []
        }
        self.config = Config.get_conf(self, identifier=42)
        self.config.register_guild(**default_guild)
        self.config.register_member(**default_member)

    @commands.command(name="signup")
    @commands.guild_only()
    async def _reg(self, ctx):
        """Sign up to get your own spellbook!"""

        server = ctx.guild
        user = ctx.author
        db = await self.config.guild(server).db()
        if user.id not in db:
            db.append(user.id)
            await self.config.guild(server).db.set(db)
            await self.sendDiscordMessage(ctx, ":mage: Congrats! :mage:", "You have created your spellbook for **{}**, {}.".format(server.name, user.mention))
        else:
            await self.sendDiscordMessage(ctx, ":warning: Error :warning:", "Opps, it seems like you already have a spellbook, {}.".format(user.mention))

    @commands.command(name="spellbook")
    @commands.guild_only()
    async def _acc(self, ctx, user: discord.Member = None):
        """Take a peek at your, or someone else's, spellbook."""

        server = ctx.guild
        prefix = ctx.prefix
        db = await self.config.guild(server).db()
        user = user if user else ctx.author
        userdata = await self.config.member(user).all()
        pic = userdata["Characterpic"]

        Pages = []
        Pageno = 1

        if user.id not in db:
            await self.sendDiscordMessage(
                ctx, ":warning: Error :warning:", "Sadly, you can't peek into other people's Spellbooks without having a spellbook first. \n\nYou can create your spellbook by saying `{}signup` and you'll be all set.".format(prefix))

        for k, v in userdata.items():
            data = discord.Embed(colour=user.colour)
            # data.set_author(name="{}'s Account".format(user.name), icon_url=user.avatar_url)
            if v and not k == "Characterpic":
                if user.avatar_url and not pic:
                    if k == "Spell":
                        for page in list(pagify(str(v), delims=[","], page_length=600, shorten_by=50)):
                            data.set_author(
                                name=f"{str(user)}'s Spellbook", url=user.avatar_url)
                            data.set_thumbnail(url=user.avatar_url)
                            page = listformatter(page)
                            data.add_field(name="Spells Known:",
                                           value=page, inline=False)
                            data.set_footer(
                                text=f"Page {Pageno} out of {len(userdata.items())}")
                            Pages.append(data)
                    else:
                        data.set_author(
                            name=f"{str(user)}'s Spellbook", url=user.avatar_url)
                        data.set_thumbnail(url=user.avatar_url)
                        data.add_field(name=k, value=v)
                        data.set_footer(
                            text=f"Page {Pageno} out of {len(userdata.items())}")
                        Pageno += 1
                        Pages.append(data)
                elif pic:
                    if k == "Spell":
                        for page in list(pagify(str(v), delims=[","], page_length=600, shorten_by=50)):
                            data.set_author(
                                name=f"{str(user)}'s Spellbook", url=user.avatar_url)
                            data.set_thumbnail(url=user.avatar_url)
                            page = listformatter(page)
                            data.add_field(name="Spells Known:",
                                           value=page, inline=False)
                            data.set_footer(
                                text=f"Page {Pageno} out of {len(userdata.items())}")
                            Pages.append(data)
                    else:
                        data.set_author(
                            name=f"{str(user)}'s Spellbook", url=user.avatar_url)
                        data.set_thumbnail(url=user.avatar_url)
                        data.add_field(name=k, value=v)
                        data.set_footer(
                            text=f"Page {Pageno} out of {len(userdata.items())}")
                        Pageno += 1
                        Pages.append(data)

        if len(Pages) != 0:
            await menu(ctx, Pages, DEFAULT_CONTROLS)
        else:
            await self.sendDiscordMessage(ctx, ":smiling_face_with_tear: Sad Wizard is sad :smiling_face_with_tear:",
                                          "{}'s Spellbook is empty.".format(user.mention))

    @commands.group(name="add")
    @commands.guild_only()
    async def add(self, ctx):
        """Update your Spellbook"""
        pass

    @add.command(name="spells")
    @commands.guild_only()
    async def addSpell(self, ctx, *, spell):
        """Which spell(s) do you want to add?"""

        # making a set so that duplicate spells in the same call are not considered
        new_spell_list = processStringToList(spell)
        new_spell_list_valid = []
        new_spell_list_invalid = []
        new_spell_list_duplicate = []
        server = ctx.guild
        user = ctx.author
        prefix = ctx.prefix
        guild_group = self.config.member(user)
        db = await self.config.guild(server).db()
        userdata = await self.config.member(user).all()

        if user.id not in db:
            await self.sendDiscordMessage(
                ctx, ":warning: Error :warning:", "Sadly, you can't add spells without having a spellbook first. \n\nYou can create your spellbook by saying `{}signup` and you'll be all set.".format(prefix))
        else:
            for new_spell in new_spell_list:
                # checks if it's a valid spell
                if not isSpellValid(new_spell):
                    new_spell_list_invalid.append(new_spell)
                    continue
                else:
                    # checks if the user already has this spell
                    if new_spell in userdata["Spell"]:
                        new_spell_list_duplicate.append(new_spell)
                        continue
                    else:
                        new_spell_list_valid.append(new_spell)
                        continue

            # save the valid spells, if any
            if(len(new_spell_list_valid) > 0):
                async with guild_group.Spell() as SpellGroup:
                    SpellGroup.extend(new_spell_list_valid)
                    SpellGroup.sort()
                    await self.sendDiscordMessage(ctx, ":sparkles: Success! :sparkles:",
                                                  "You have copied the following {} into your Spellbook:\n{}".format("spells" if(len(new_spell_list_valid) > 1) else "spell", ", ".join(new_spell_list_valid)))

            # send the duplicate spells, if any
            if(len(new_spell_list_duplicate) > 0):
                await self.sendDiscordMessage(ctx, ":coin: I'm saving you money! :coin:",
                                              "You already had {} in your Spellbook: \n{}".format("these spells" if(len(new_spell_list_duplicate) > 1) else "this spell", ", ".join(new_spell_list_duplicate)))

            # send the invalid spells, if any
            if(len(new_spell_list_invalid) > 0):
                await self.sendDiscordMessage(ctx, ":warning: Oh no! :warning:",
                                              "The following {} not valid:\n{}\nPlease make sure you spelled it right\nUsed ' and -'s correctly.\nPlease make sure your spell is in [this list](https://pastebin.com/YS7NmYqh)".format("spells are" if(len(new_spell_list_invalid) > 1) else "spell is", ", ".join(new_spell_list_invalid)))

    @commands.group(name="remove")
    @commands.guild_only()
    async def remove(self, ctx):
        """Rips pages from your Spellbook"""
        pass

    @remove.command(name="spells")
    @commands.guild_only()
    async def removeSpells(self, ctx, *, spell):
        """Rip pages from your spellbook, as hard as it is to do it"""

        # making a set so that duplicate spells in the same call are not considered
        new_spell_list = processStringToList(spell)
        new_spell_list_valid = []
        new_spell_list_invalid = []
        new_spell_list_unlearned = []
        server = ctx.guild
        user = ctx.author
        prefix = ctx.prefix
        db = await self.config.guild(server).db()
        guild_group = self.config.member(user)
        userdata = await self.config.member(user).all()

        if user.id not in db:
            await self.sendDiscordMessage(
                ctx, ":warning: Error :warning:", "Sadly, you can't add spells without having a spellbook first. \n\nYou can create your spellbook by saying `{}signup` and you'll be all set.".format(prefix))
        else:
            for new_spell in new_spell_list:
                # checks if it's a valid spell
                if not isSpellValid(new_spell):
                    new_spell_list_invalid.append(new_spell)
                    continue
                else:
                    # checks if the user already has this spell
                    if new_spell in userdata["Spell"]:
                        new_spell_list_valid.append(new_spell)
                        continue
                    else:
                        new_spell_list_unlearned.append(new_spell)
                        continue

                        # send the valid spells, if any
            if(len(new_spell_list_valid) > 0):
                async with guild_group.Spell() as SpellGroup:
                    for spell in new_spell_list_valid:
                        try:
                            SpellGroup.remove(spell)
                        except ValueError:
                            new_spell_list_valid.remove(spell)
                            pass
                    SpellGroup.sort()
                    await self.sendDiscordMessage(ctx, ":sob: Success :sob:", "You have ripped the pages of the following {} from your Spellbook:\n{}".format("spells" if(len(new_spell_list_valid) > 1) else "spell", ", ".join(new_spell_list_valid)))

            # send the duplicate spells, if any
            if(len(new_spell_list_unlearned) > 0):
                await self.sendDiscordMessage(ctx, ":question: Hmm? :question:", "You don't have {} in your Spellbook:\n{}".format("these spells" if(len(new_spell_list_unlearned) > 1) else "this spell",
                                                                                                                                   ", ".join(new_spell_list_unlearned)))

                # send the invalid spells, if any
            if(len(new_spell_list_invalid) > 0):
                await self.sendDiscordMessage(
                    ctx, ":warning: Oh no! :warning:", "The following {} not valid:\n{}\nPlease make sure you spelled it right\nUsed ' and -'s correctly.\nPlease make sure your spell is in [this list](https://pastebin.com/YS7NmYqh)".format("spells are" if (len(new_spell_list_invalid)) else "spell is", " ".join(new_spell_list_invalid)))

    @commands.command()
    @commands.guild_only()
    @spellbook.command()
    async def filter(self, ctx, category):
        """
        Filter your spells by category.
        """
        category = category.lower()
        if category not in SPELL_CATEGORIES:
            return await ctx.send("Invalid category. Use `;category` command to see all available categories.")
        
        spells = self.get_spells(ctx.author.id)
        if not spells:
            return await ctx.send("You don't have any spells yet.")
        
        filtered_spells = [spell for spell in spells if spell["category"] == category]
        
        if not filtered_spells:
            return await ctx.send("You don't have any spells in this category.")
        
        filtered_spells = sorted(filtered_spells, key=lambda x: x["name"])
        
        filtered_spells_str = "\n".join([f'**{spell["name"]}**: {spell["description"]}' for spell in filtered_spells])
        
        # Fix for 'NoneType' object has no attribute 'display_name' error
        user = ctx.author
        if ctx.message.mentions:
            user = ctx.message.mentions[0]
        nickname = user.display_name if user else "Unknown User"
        
        embed = discord.Embed(title=f"{nickname}'s {category.capitalize()} Spells", description=filtered_spells_str, color=0x4a90e2)
        await ctx.send(embed=embed)


    async def sendDiscordMessage(self, ctx, title, text):
        data = discord.Embed(colour=ctx.author.colour)
        data.add_field(name=title, value=text)
        await ctx.send(embed=data)
