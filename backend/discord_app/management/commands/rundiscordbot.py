# this file contains main bot logic to handle bot command such as sending anoymous messages and undoing them  
import discord
from discord_app.models import AnonymousMessage
from social_django.models import UserSocialAuth
from django.core.management.base import BaseCommand
from django.conf import settings

class Client(discord.Client):
    async def on_ready(self):
        print(f'Logged on as {self.user}!')

    async def on_interaction(self, interaction):
        try:
            if interaction.data['name'] == 'anon':
                await self.handle_anon_command(interaction)
            elif interaction.data['name'] == 'undo':
                await self.handle_undo_command(interaction)
        except Exception as e:
            print(e)
            await interaction.response.send_message('An error occurred', ephemeral=True)

    async def handle_anon_command(self, interaction):
        options = interaction.data['options']
        assert len(options) == 1
        assert options[0]['name'] == 'message'
        content = options[0]['value']
        message = await interaction.channel.send(content)
        discord_user_id = interaction.user.id
        model = AnonymousMessage(
            discord_user_id=discord_user_id,
            discord_channel_id=interaction.channel.id,  
            discord_guild_id=interaction.guild.id,     
            discord_message_id=message.id,
            content=content,
            undid=False,
        )
        try:
            social_auth = await UserSocialAuth.objects \
                                .select_related('user') \
                                .aget(
                                    provider='discord',
                                    uid=discord_user_id
                                )
            model.user = social_auth.user
        except UserSocialAuth.DoesNotExist:
            pass
        await model.asave()
        await interaction.response.send_message(f'You sent: "{content}"', ephemeral=True)

    async def handle_undo_command(self, interaction):
        discord_user_id = interaction.user.id
        discord_channel_id = interaction.channel.id
        try:
            # Find the latest non-undone message by this user in the current channel
            latest_message = await AnonymousMessage.objects \
                .filter(discord_user_id=discord_user_id, discord_channel_id=discord_channel_id, undid=False) \
                .order_by('-sent') \
                .afirst()

            if latest_message:
                # Mark the message as undone in the database
                latest_message.undid = True
                await latest_message.asave()
                
                # Delete the message from the Discord channel
                channel = interaction.channel
                discord_message = await channel.fetch_message(latest_message.discord_message_id)
                await discord_message.delete()

                await interaction.response.send_message(f'Your message "{latest_message.content}" has been undone.', ephemeral=True)
            else:
                await interaction.response.send_message('Nothing to undo.', ephemeral=True)
        except Exception as e:
            print(f'Error in undo command: {e}')
            await interaction.response.send_message('An error occurred while trying to undo your message.', ephemeral=True)

class Command(BaseCommand):
    help = 'Run Discord Bot'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting Discord Bot...'))
        intents = discord.Intents.default()
        client = Client(intents=intents)
        client.run(settings.DISCORD_BOT_TOKEN)
