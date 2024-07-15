from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

import discord

from discord_app.models import AnonymousMessage
from social_django.models import UserSocialAuth

class Client(discord.Client):

    async def on_ready(self):
        print(f'Logged on as {self.user}!')

    async def on_interaction(self, interaction):
        try:
            options = interaction.data['options']
            assert len(options) == 1
            assert options[0]['name'] == 'message'
            content = options[0]['value']
            message = await interaction.channel.send(content)
            discord_user_id = interaction.user.id
            model = AnonymousMessage(
                discord_user_id=discord_user_id,
                channel_id=interaction.channel_id,
                guild_id=interaction.guild_id,
                message_id=message.id,
                content=content,
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
            await interaction.response.send_message(
                f'You sent: "{content}"', ephemeral=True
            )
        except KeyError as e:
            await interaction.response.send_message(
                'You need to type a message', ephemeral=True
            )
        except Exception as e:
            print(e)
            await interaction.response.send_message(
                'An error occurred', ephemeral=True
            )

class Command(BaseCommand):
    help = "Run Discord Bot"

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        intents = discord.Intents.default()
        # intents.message_content = True

        client = Client(intents=intents)
        client.run(settings.DISCORD_BOT_TOKEN)
