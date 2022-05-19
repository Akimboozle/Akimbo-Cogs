from .spellbook import Spellbook


def setup(bot):
    bot.add_cog(Spellbook(bot))
