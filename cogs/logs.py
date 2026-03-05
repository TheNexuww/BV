import discord
from discord import app_commands
from discord.ext import commands
from utils.config import get_logs_channel, set_logs_channel
from datetime import datetime


class ChannelSelectMenu(discord.ui.View):
    """View avec un select menu pour choisir le channel."""
    
    def __init__(self, guild: discord.Guild):
        super().__init__()
        self.guild = guild
        
        # Créer le select menu avec les channels texte du serveur
        options = []
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                options.append(
                    discord.SelectOption(
                        label=channel.name,
                        value=str(channel.id),
                        description=f"ID: {channel.id}"
                    )
                )
        
        if options:
            self.select_menu.options = options
            self.add_item(self.select_menu)
    
    @discord.ui.select(
        placeholder="Choisir un channel pour les logs...",
        min_values=1,
        max_values=1
    )
    async def select_menu(self, interaction: discord.Interaction, select: discord.ui.Select):
        channel_id = int(select.values[0])
        set_logs_channel(interaction.guild_id, channel_id)
        
        channel = self.guild.get_channel(channel_id)
        embed = discord.Embed(
            title="✅ Configuration sauvegardée",
            description=f"Les logs seront envoyés dans {channel.mention}",
            color=discord.Color.green(),
            timestamp=datetime.now()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


class LogsCog(commands.Cog):
    """Cog pour la gestion des logs du serveur."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def send_log(self, guild: discord.Guild, embed: discord.Embed):
        """Envoyer un message de log au channel configuré."""
        channel_id = get_logs_channel(guild.id)
        if not channel_id:
            return
        
        channel = guild.get_channel(channel_id)
        if channel:
            try:
                await channel.send(embed=embed)
            except discord.Forbidden:
                pass

    @app_commands.command(name="logsconfig", description="Configure le channel pour les logs")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def logs_config(self, interaction: discord.Interaction):
        """Ouvrir l'interface de configuration des logs."""
        view = ChannelSelectMenu(interaction.guild)
        
        embed = discord.Embed(
            title="⚙️ Configuration des Logs",
            description="Sélectionne le channel où tu veux que les logs apparaissent.",
            color=discord.Color.blue()
        )
        
        await interaction.response.send_message(
            embed=embed,
            view=view,
            ephemeral=True
        )

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """Enregistrer quand un membre rejoint le serveur."""
        embed = discord.Embed(
            title="✅ Nouveau membre",
            description=f"{member.mention} a rejoint le serveur",
            color=discord.Color.green(),
            timestamp=datetime.now()
        )
        embed.set_thumbnail(url=member.avatar.url if member.avatar else "")
        embed.add_field(name="Utilisateur", value=f"{member.name}#{member.discriminator}", inline=False)
        embed.add_field(name="ID", value=member.id, inline=False)
        embed.add_field(name="Compte créé", value=f"<t:{int(member.created_at.timestamp())}:f>", inline=False)
        
        await self.send_log(member.guild, embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        """Enregistrer quand un membre quitte le serveur."""
        embed = discord.Embed(
            title="❌ Membre parti",
            description=f"{member.name} a quitté le serveur",
            color=discord.Color.red(),
            timestamp=datetime.now()
        )
        embed.set_thumbnail(url=member.avatar.url if member.avatar else "")
        embed.add_field(name="Utilisateur", value=f"{member.name}#{member.discriminator}", inline=False)
        embed.add_field(name="ID", value=member.id, inline=False)
        
        await self.send_log(member.guild, embed)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        """Enregistrer les changements d'état vocal."""
        # Cas 1: Rejoint un salon vocal
        if before.channel is None and after.channel is not None:
            embed = discord.Embed(
                title="🎙️ Rejoint un salon vocal",
                description=f"{member.mention} a rejoint {after.channel.mention}",
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )
            embed.set_thumbnail(url=member.avatar.url if member.avatar else "")
            embed.add_field(name="Utilisateur", value=f"{member.name}#{member.discriminator}", inline=False)
            embed.add_field(name="Salon vocal", value=after.channel.name, inline=False)
            
            await self.send_log(member.guild, embed)
        
        # Cas 2: Quitte un salon vocal
        elif before.channel is not None and after.channel is None:
            embed = discord.Embed(
                title="🎙️ Quitté un salon vocal",
                description=f"{member.name} a quitté {before.channel.mention}",
                color=discord.Color.orange(),
                timestamp=datetime.now()
            )
            embed.set_thumbnail(url=member.avatar.url if member.avatar else "")
            embed.add_field(name="Utilisateur", value=f"{member.name}#{member.discriminator}", inline=False)
            embed.add_field(name="Salon vocal", value=before.channel.name, inline=False)
            
            await self.send_log(member.guild, embed)
        
        # Cas 3: Changé de salon vocal
        elif before.channel != after.channel:
            embed = discord.Embed(
                title="🎙️ Changé de salon vocal",
                description=f"{member.mention} est passé de {before.channel.mention} à {after.channel.mention}",
                color=discord.Color.purple(),
                timestamp=datetime.now()
            )
            embed.set_thumbnail(url=member.avatar.url if member.avatar else "")
            embed.add_field(name="Utilisateur", value=f"{member.name}#{member.discriminator}", inline=False)
            embed.add_field(name="De", value=before.channel.name, inline=True)
            embed.add_field(name="Vers", value=after.channel.name, inline=True)
            
            await self.send_log(member.guild, embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        """Enregistrer quand un message est supprimé."""
        if message.author.bot:
            return
        
        embed = discord.Embed(
            title="🗑️ Message supprimé",
            description=f"Message supprimé par {message.author.mention}",
            color=discord.Color.red(),
            timestamp=datetime.now()
        )
        embed.set_thumbnail(url=message.author.avatar.url if message.author.avatar else "")
        embed.add_field(name="Auteur", value=f"{message.author.name}#{message.author.discriminator}", inline=False)
        embed.add_field(name="Channel", value=message.channel.mention, inline=False)
        embed.add_field(name="Contenu", value=message.content[:1024] if message.content else "*Aucun contenu*", inline=False)
        
        await self.send_log(message.guild, embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        """Enregistrer quand un message est édité."""
        if after.author.bot or before.content == after.content:
            return
        
        embed = discord.Embed(
            title="✏️ Message édité",
            description=f"Message édité par {after.author.mention}",
            color=discord.Color.yellow(),
            timestamp=datetime.now()
        )
        embed.set_thumbnail(url=after.author.avatar.url if after.author.avatar else "")
        embed.add_field(name="Auteur", value=f"{after.author.name}#{after.author.discriminator}", inline=False)
        embed.add_field(name="Channel", value=after.channel.mention, inline=False)
        embed.add_field(name="Avant", value=before.content[:512] if before.content else "*Aucun contenu*", inline=False)
        embed.add_field(name="Après", value=after.content[:512] if after.content else "*Aucun contenu*", inline=False)
        
        await self.send_log(after.guild, embed)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        """Enregistrer quand quelqu'un ajoute une réaction."""
        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            return
        
        channel = guild.get_channel(payload.channel_id)
        if not channel:
            return
        
        try:
            message = await channel.fetch_message(payload.message_id)
        except discord.NotFound:
            return
        
        user = self.bot.get_user(payload.user_id)
        if user and user.bot:
            return
        
        embed = discord.Embed(
            title="👍 Réaction ajoutée",
            description=f"{user.mention} a réagi avec {payload.emoji}",
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        embed.set_thumbnail(url=user.avatar.url if user.avatar else "")
        embed.add_field(name="Utilisateur", value=f"{user.name}#{user.discriminator}", inline=False)
        embed.add_field(name="Channel", value=channel.mention, inline=False)
        embed.add_field(name="Message", value=message.content[:256] if message.content else "*Pas de contenu*", inline=False)
        
        await self.send_log(guild, embed)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        """Enregistrer quand quelqu'un retire une réaction."""
        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            return
        
        user = self.bot.get_user(payload.user_id)
        if user and user.bot:
            return
        
        channel = guild.get_channel(payload.channel_id)
        if not channel:
            return
        
        embed = discord.Embed(
            title="👎 Réaction retirée",
            description=f"{user.mention} a retiré sa réaction {payload.emoji}",
            color=discord.Color.purple(),
            timestamp=datetime.now()
        )
        embed.set_thumbnail(url=user.avatar.url if user.avatar else "")
        embed.add_field(name="Utilisateur", value=f"{user.name}#{user.discriminator}", inline=False)
        embed.add_field(name="Channel", value=channel.mention, inline=False)
        
        await self.send_log(guild, embed)

    @logs_config.error
    async def logs_config_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        """Gérer les erreurs de permission."""
        if isinstance(error, app_commands.MissingPermissions):
            embed = discord.Embed(
                title="❌ Permission refusée",
                description="Tu dois être modérateur pour utiliser cette commande.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    """Charger le cog."""
    await bot.add_cog(LogsCog(bot))
