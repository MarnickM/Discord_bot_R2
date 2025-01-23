import os, json, time, threading
import discord
from discord import channel
from discord import app_commands
from discord.ui import Button
from discord.ext import commands
from datetime import datetime, timedelta, timezone
from itertools import islice
import typing
from discord.ext import tasks
import asyncio
import aiohttp
from dotenv import load_dotenv
import re
from itertools import groupby
import io
import openpyxl

load_dotenv()

from database import database
from dropdown import dropdown

db_operations = database.DatabaseConnection()

admin = int(os.getenv('admin'))
global organizer_channel_id 
organizer_channel_id = int(os.getenv('organizer_channel_id'))
global events_category_id
events_category_id = int(os.getenv('events_category_id'))
global archive_category_id
archive_category_id = int(os.getenv('archive_category_id'))
global event_organizer_id
event_organizer_id = int(os.getenv('event_organizer_id'))
global image_dir
image_dir = os.getenv('image_dir')

# set up the bot
bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

@bot.event
async def on_ready():
    print('Bot is ready')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands.")
    except Exception as e:
        print(f"Failed to sync commands: {e}")


# sync commands
@bot.command()
async def sync(ctx) -> None:
  guild = bot.get_guild(int(os.getenv('serverID')))
  synced = await bot.tree.sync(guild=guild)
  print(f"Synced {len(synced)} commands.")


async def event_suggestions(interaction: discord.Interaction, event: str) -> typing.List[app_commands.Choice[str]]:
    events = db_operations.get_events(event)
    suggestions = [app_commands.Choice(name=name, value=name) for name in events]
    return suggestions

async def droid_suggestions(interaction: discord.Interaction, event: str) -> typing.List[app_commands.Choice[str]]:
    events = db_operations.get_droids(event)
    suggestions = [app_commands.Choice(name=name, value=name) for name in events]
    return suggestions

async def registered_suggestions(interaction: discord.Interaction, event: str) -> typing.List[app_commands.Choice[str]]:
    user = interaction.user
    events = db_operations.get_registered_events(event, user.name)
    suggestions = [app_commands.Choice(name=name, value=name) for name in events]
    return suggestions

async def user_suggestions(interaction: discord.Interaction, user: str) -> typing.List[app_commands.Choice[str]]:
    users = db_operations.get_users(user)
    suggestions = [app_commands.Choice(name=name, value=name) for name in users]
    return suggestions

async def non_discord_suggestions(interaction: discord.Interaction, user: str) -> typing.List[app_commands.Choice[str]]:
    users = db_operations.get_non_discord_users(user)
    suggestions = [app_commands.Choice(name=name, value=name) for name in users]
    return suggestions

async def status_suggestions(interaction: discord.Interaction, status: str) -> typing.List[app_commands.Choice[str]]:
    return [
        app_commands.Choice(name="Confirmed", value="confirmed"),
        app_commands.Choice(name="Declined", value="declined")
    ]

async def amenity_suggestions(interaction: discord.Interaction, event: str) -> typing.List[app_commands.Choice[str]]:
    amenities = db_operations.get_amenities(event)
    suggestions = [app_commands.Choice(name=name, value=name) for name in amenities]
    return suggestions


# create a suggestion for the image names in the /image folder
async def image_suggestions(interaction: discord.Interaction, image: str) -> typing.List[app_commands.Choice[str]]:
    global image_dir
    images = os.listdir(image_dir)
    suggestions = [app_commands.Choice(name=name, value=name) for name in images]
    return suggestions



def nsfw_check(interaction: discord.Interaction) -> bool:
    """Checks if the command is being run in an NSFW channel."""
    return interaction.channel.is_nsfw()



# Get the role IDs from the environment
ROLE_IDS = {
    "FR": os.getenv("role_FR"),
    "EN": os.getenv("role_EN"),
    "DE": os.getenv("role_DE"),
    "NL": os.getenv("role_NL"),
    "BE": os.getenv("role_BE"),  # Add BE for the NL embed
}


def convert_date_to_eu(us_date):
    """Converts a date from YYYY-MM-DD (US) to DD-MM-YYYY (EU)."""
    date_obj = datetime.strptime(us_date, "%Y-%m-%d")
    return date_obj.strftime("%d-%m-%Y")

def format_date_localized(us_date, lang):
    """Converts a date from YYYY-MM-DD (US) to a localized format."""
    date_obj = datetime.strptime(us_date, "%Y-%m-%d")
    day = date_obj.day
    month = date_obj.strftime("%B")  # Full month name
    year = date_obj.year
    
    if lang == "EN":
        # Add English ordinal suffix
        suffix = "th" if 11 <= day <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
        return f"{day}{suffix} of {month} {year}"
    elif lang == "NL":
        # Dutch ordinal suffix
        return f"{day}de {month} {year}"
    elif lang == "FR":
        # French ordinal (no suffix for most dates)
        suffix = "er" if day == 1 else ""
        return f"{day}{suffix} {month} {year}"
    elif lang == "DE":
        # German format
        return f"{day}. {month} {year}"
    else:
        # Default to English if language not recognized
        return f"{day}th of {month} {year}"


def translate_day_name(day_name, lang):
    """
    Translates an English day name into the specified language.

    :param day_name: The English name of the day (e.g., 'Monday').
    :param lang: The target language code (e.g., 'FR', 'DE', 'NL').
    :return: The translated day name.
    """
    format = False
    
    # Check if the day_name string contains a comma (i.e., dayname, HH:MM)
    if "," in day_name:
        day_parts = day_name.split(",")  # Split into [dayname, time]
        
        if len(day_parts) == 2:
            day_name = day_parts[0].strip()  # Get the day part and remove extra spaces
            format = True
            time = day_parts[1].strip()  # Get the time part
            
            #print(f"Day: {day_name}, Time: {time}")
        else:
            # Handle the case where the split doesn't result in two parts (for edge cases)
            print(f"Unexpected format in day_name: {day_name}")
            return day_name  # Return the original day_name if there's an issue

    translations = {
        "Monday": {"FR": "Lundi", "DE": "Montag", "NL": "Maandag"},
        "Tuesday": {"FR": "Mardi", "DE": "Dienstag", "NL": "Dinsdag"},
        "Wednesday": {"FR": "Mercredi", "DE": "Mittwoch", "NL": "Woensdag"},
        "Thursday": {"FR": "Jeudi", "DE": "Donnerstag", "NL": "Donderdag"},
        "Friday": {"FR": "Vendredi", "DE": "Freitag", "NL": "Vrijdag"},
        "Saturday": {"FR": "Samedi", "DE": "Samstag", "NL": "Zaterdag"},
        "Sunday": {"FR": "Dimanche", "DE": "Sonntag", "NL": "Zondag"},
    }

    translation = translations.get(day_name, {}).get(lang, day_name)
    
    if format:
        # If time was present, return the translated day with time
        return f"{translation}, {time}"
    
    return translation


   
# Helper function to get server nickname or fallback to participant name
def get_server_nickname(participant_name):
    user = db_operations.get_user(participant_name)
    if user:
        return user.get('server_nickname', participant_name)
    else:
        return participant_name  # Return the participant name if not found in the database
   
    


@bot.tree.command(name='events_in_languages', description='(admin only) Initiate the registration for an event')
@app_commands.checks.has_any_role(admin)
@app_commands.autocomplete(event=event_suggestions)
@app_commands.describe(event="The name of the event")
async def events_in_languages(interaction: discord.Interaction, event: str):
    try: 

        global image_dir
        # Defer the response so that the bot can send follow-ups later
        await interaction.response.defer()
        global organizer_channel_id
    
        event_details = db_operations.get_event(event)
        if not event_details:
            await interaction.followup.send('Event not found')
            return
        
        # Generate the embeds in all available languages
        embeds = []
        for lang in ["FR", "EN", "DE", "NL"]:  # Loop over all languages
            embed = discord.Embed(title=event_details['name'], description=event_details['description'], color=0x4c65f1)
    
            # # Set the event photo as a thumbnail, if available
            # photo_url = event_details.get('photo_url')
            # file = None
            # if photo_url:
            #         # Prepare the image path
            #         file_path = f'{image_dir}/{photo_url}'
        
            #         # Check if the file exists
            #         if os.path.exists(file_path):
            #             with open(file_path, 'rb') as f:
            #                 file = discord.File(f, filename=f"{photo_url}")  # Upload the file
            #                 embed.set_thumbnail(url=f"attachment://{file.filename}")  # Set thumbnail as attachment
        
            #             # Add the image as an attachment
            #             embed.set_thumbnail(url=f"attachment://{file.filename}")
            #         else:
            #             # Set a fallback image if the file does not exist
            #             embed.set_thumbnail(url="https://example.com/default-thumbnail.jpg")  # Fallback thumbnail
            if lang == "FR":
                embed.add_field(name="📍 Localisation", value=f"{event_details['location']['venue']}\n{event_details['location']['address']['street']}, {event_details['location']['address']['postal_code']} {event_details['location']['address']['city']}, {event_details['location']['address']['country']}", inline=False)
                embed.add_field(
                   name="📅 Dates",
                   value=(
                       f"{event_details['dates'][0]['open_time']} à {event_details['dates'][0]['close_time']} - "
                       f"{translate_day_name(event_details['dates'][0]['day'], 'FR')} {format_date_localized(event_details['dates'][0]['date'], 'FR')}\n"
                       f"{event_details['dates'][1]['open_time']} à {event_details['dates'][1]['close_time']} - "
                       f"{translate_day_name(event_details['dates'][1]['day'], 'FR')} {format_date_localized(event_details['dates'][1]['date'], 'FR')}"
                   ),
                   inline=False
                )
                embed.add_field(name="⏰ Heure d'arrivée", value=translate_day_name(event_details['attendance_requirements']['arrival_time'], 'FR'), inline=True)
                embed.add_field(name="👨‍💼 Organisateur", value=event_details['organizer']['name'], inline=True)
                embed.add_field(name="📅 Date limite d'inscription", value=convert_date_to_eu(event_details['registration_deadline']), inline=False)
                embed.add_field(name="🎫 Exigences de présence", value=event_details['attendance_requirements']['note'] if event_details['attendance_requirements']['note'] else "Aucune", inline=False)
                embed.add_field(name="✅ Participants Confirmés", value="\n".join(map(get_server_nickname, event_details['participants']['confirmed'])) if event_details['participants']['confirmed'] else "Aucun", inline=False)
                embed.add_field(name="❌ Participants Déclinés", value="\n".join(map(get_server_nickname, event_details['participants']['declined'])) if event_details['participants']['declined'] else "Aucun", inline=False)
            elif lang == "EN":
                embed.add_field(name="📍 Location", value=f"{event_details['location']['venue']}\n{event_details['location']['address']['street']}, {event_details['location']['address']['postal_code']} {event_details['location']['address']['city']}, {event_details['location']['address']['country']}", inline=False)
                embed.add_field(
                    name="📅 Event Dates",
                    value=f"{event_details['dates'][0]['open_time']} to {event_details['dates'][0]['close_time']} - "
                          f"{event_details['dates'][0]['day']} {format_date_localized(event_details['dates'][0]['date'], 'EN')}\n"
                          f"{event_details['dates'][1]['open_time']} to {event_details['dates'][1]['close_time']} - "
                          f"{event_details['dates'][1]['day']} {format_date_localized(event_details['dates'][1]['date'], 'EN')}",
                    inline=False
                )
                embed.add_field(name="⏰ Arrival Time", value=event_details['attendance_requirements']['arrival_time'], inline=True)
                embed.add_field(name="👨‍💼 Organizer", value=event_details['organizer']['name'], inline=True)
                embed.add_field(name="📅 Registration Deadline", value=convert_date_to_eu(event_details['registration_deadline']), inline=False)
                embed.add_field(name="🎫 Attendance Requirements", value=event_details['attendance_requirements']['note'] if event_details['attendance_requirements']['note'] else "None", inline=False)
                embed.add_field(name="✅ Confirmed Participants", value="\n".join(map(get_server_nickname, event_details['participants']['confirmed'])) if event_details['participants']['confirmed'] else "None", inline=False)
                embed.add_field(name="❌ Declined Participants", value="\n".join(map(get_server_nickname, event_details['participants']['declined'])) if event_details['participants']['declined'] else "None", inline=False)
            elif lang == "DE":
                embed.add_field(name="📍 Ort", value=f"{event_details['location']['venue']}\n{event_details['location']['address']['street']}, {event_details['location']['address']['postal_code']} {event_details['location']['address']['city']}, {event_details['location']['address']['country']}", inline=False)
                embed.add_field(
                    name="📅 Event Termine",
                    value=f"{event_details['dates'][0]['open_time']} bis {event_details['dates'][0]['close_time']} - "
                          f"{translate_day_name(event_details['dates'][0]['day'], 'DE')} {format_date_localized(event_details['dates'][0]['date'], 'DE')}\n"
                          f"{event_details['dates'][1]['open_time']} bis {event_details['dates'][1]['close_time']} - "
                          f"{translate_day_name(event_details['dates'][1]['day'], 'DE')} {format_date_localized(event_details['dates'][1]['date'], 'DE')}",
                    inline=False
                )
                embed.add_field(name="⏰ Ankunftszeit", value=translate_day_name(event_details['attendance_requirements']['arrival_time'], 'DE'), inline=True)
                embed.add_field(name="👨‍💼 Organisator", value=event_details['organizer']['name'], inline=True)
                embed.add_field(name="📅 Anmeldeschluss", value=convert_date_to_eu(event_details['registration_deadline']), inline=False)
                embed.add_field(name="🎫 Teilnahmebedingungen", value=event_details['attendance_requirements']['note'] if event_details['attendance_requirements']['note'] else "Keine", inline=False)
                embed.add_field(name="✅ Bestätigte Teilnehmer", value="\n".join(map(get_server_nickname, event_details['participants']['confirmed'])) if event_details['participants']['confirmed'] else "Keine", inline=False)
                embed.add_field(name="❌ Abgelehnte Teilnehmer", value="\n".join(map(get_server_nickname, event_details['participants']['declined'])) if event_details['participants']['declined'] else "Keine", inline=False)
            elif lang == "NL":
                embed.add_field(name="📍 Locatie", value=f"{event_details['location']['venue']}\n{event_details['location']['address']['street']}, {event_details['location']['address']['postal_code']} {event_details['location']['address']['city']}, {event_details['location']['address']['country']}", inline=False)
                embed.add_field(
                    name="📅 Evenement Data",
                    value=f"{event_details['dates'][0]['open_time']} tot {event_details['dates'][0]['close_time']} - "
                          f"{translate_day_name(event_details['dates'][0]['day'], 'NL')} {format_date_localized(event_details['dates'][0]['date'], 'NL')}\n"
                          f"{event_details['dates'][1]['open_time']} tot {event_details['dates'][1]['close_time']} - "
                          f"{translate_day_name(event_details['dates'][1]['day'], 'NL')} {format_date_localized(event_details['dates'][1]['date'], 'NL')}",
                    inline=False
                )
                embed.add_field(name="⏰ Aankomsttijd", value=translate_day_name(event_details['attendance_requirements']['arrival_time'], 'NL'), inline=True)
                embed.add_field(name="👨‍💼 Organisator", value=event_details['organizer']['name'], inline=True)
                embed.add_field(name="📅 Aanmeldingsdeadline", value=convert_date_to_eu(event_details['registration_deadline']), inline=False)
                embed.add_field(name="🎫 Deelnamevereisten", value=event_details['attendance_requirements']['note'] if event_details['attendance_requirements']['note'] else "Geen", inline=False)
                embed.add_field(name="✅ Bevestigde Deelnemers", value="\n".join(map(get_server_nickname, event_details['participants']['confirmed'])) if event_details['participants']['confirmed'] else "Geen", inline=False)
                embed.add_field(name="❌ Afgewezen Deelnemers", value="\n".join(map(get_server_nickname, event_details['participants']['declined'])) if event_details['participants']['declined'] else "Geen", inline=False)
    
            embeds.append(embed)
    
        # Send the first embed with role pings in the message text
        await interaction.followup.send(
            content=f"<@&{ROLE_IDS['FR']}>",  # Mention the role
            embed=embeds[0]
        )
    
        # Send the second embed with role pings in the message text
        await interaction.followup.send(
            content=f"<@&{ROLE_IDS['EN']}>",  # Mention the role
            embed=embeds[1]
        )
    
        # Send the third embed with role pings in the message text
        await interaction.followup.send(
            content=f"<@&{ROLE_IDS['DE']}>",  # Mention the role
            embed=embeds[2]
        )
    
        # Send the fourth embed with role pings in the message text (NL + BE)
        await interaction.followup.send(
            content=f"<@&{ROLE_IDS['NL']}>, <@&{ROLE_IDS['BE']}>",  # Mention both roles for NL and BE
            embed=embeds[3]
        )
        
        # Add the question embed and dropdown
        question_embed = discord.Embed(
            title=f"Will you be attending the event: {event}?",
            description="Please select your response below:",
            color=0x4c65f1
        )
        
        event_dropdown = dropdown.EventResponseDropdown(event_name=event_details['name'])
        await interaction.followup.send(embed=question_embed, view=event_dropdown)

    except Exception as e:
        await interaction.followup.send(f"An error occurred in event_in_languages: {str(e)}")



























@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.data.get("custom_id", "").startswith("special_amenity_response_"):
        try:
            # Extract the event name and amenity name from the custom_id
            custom_id = interaction.data.get("custom_id")
            prefix = "special_amenity_response_"
            identifier = custom_id[len(prefix):]  # Remove the prefix to extract the relevant part

            # Split the identifier into event name and amenity name
            parts = identifier.split("_", 1)  # Split only once after the prefix
            if len(parts) < 2:
                await interaction.response.send_message("Invalid custom ID format.", ephemeral=True)
                return

            event_name, amenity_name = parts[0], parts[1]
            event_name = event_name.replace("_", " ").strip()  # Replace underscores with spaces
            amenity_name = amenity_name.replace("_", " ").strip()  # Replace underscores with spaces

            # print(f"event_name: {event_name}, amenity_name: {amenity_name}")

            # Get the selected response from the dropdown
            status = interaction.data.get("values")[0]
            response_mapping = {
                "yes": "will come (✅) to ",
                "no": "will not come (❌) to",
                "not_sure": "might come (⚠️), but are not sure yet, to"
            }
            readable_response = response_mapping.get(status, "gave an unknown response")

            # Add the user to the correct status category
            user_name = interaction.user.display_name
            added = db_operations.add_user_to_amenity(
                discord_name=user_name,
                event_name=event_name,
                amenity_name=amenity_name,
                status=status
            )

            # Check if the user is already registered
            username = interaction.user.name
    
            user = db_operations.get_user(username)
            if not user:
                await interaction.response.send_message(
                    "⚠️ You are not registered yet. Please use the `/register` command to register first.",
                    ephemeral=True
                )
            
            if added:
                await interaction.response.send_message(
                    f"✅ Thank you! You have been added to the '{amenity_name}' activity for the event: **{event_name}** with status: **{status}**.",
                    ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    f"❌ You are already registered for the '{amenity_name}' activity for the event: **{event_name}**.",
                    ephemeral=True
                )

            # Save the dropdown message's custom_id into the message_ids collection
            db_operations.add_message_id(custom_id, amenity_name, interaction.channel.id)

            # Optionally, send a message to the organizer channel
            organizers_channel = bot.get_channel(organizer_channel_id)
            if organizers_channel:
                await organizers_channel.send(
                    f"🍴🍔 **ACTIVITY** >>> **{interaction.user.display_name}** {readable_response} the activity: **{amenity_name}**."
                )

        except Exception as e:
            await interaction.response.send_message(f"An error occurred in on_interaction, activity dropdown: {str(e)}", ephemeral=True)


    try: 
        # for events
        # Check if the interaction is a dropdown menu
        if interaction.data.get("custom_id", "").startswith("event_response_"):
            # Extract the custom_id, which contains the event_name
            custom_id = interaction.data.get("custom_id")
            event_name = custom_id.replace("event_response_", "")
    
            # Get the response (Yes, No, or Not Sure)
            response = interaction.data.get("values")[0]
            response_mapping = {
                "yes": "will come (✅) to ",
                "no": "will not come (❌) to",
                "not_sure": "might come (⚠️), but are not sure yet, to"
            }
            readable_response = response_mapping.get(response, "gave an unknown response")
    
            # Send an acknowledgment to the user
            await interaction.response.send_message(
                f"✅ Thank you! We've noted that you {readable_response} the event: **{event_name}**.",
                ephemeral=True
            )
    
            # Check if the user is already registered
            username = interaction.user.name
    
            user = db_operations.get_user(username)
            if not user:
                await interaction.response.send_message(
                    "⚠️ You are not registered yet. Please use the `/register` command to register first.",
                    ephemeral=True
                )
                return  # Exit early if the user is not registered
    
            # Add the user's response to the event's participants
            if response == "yes":
                db_operations.add_participant_to_event(event_name, username, "confirmed")
            elif response == "no":
                db_operations.add_participant_to_event(event_name, username, "declined")
            elif response == "not_sure":
                db_operations.add_participant_to_event(event_name, username, "pending")
    
            # Add the user to the event's "events" array in the user document
            droid_count = 0  # Default value if not provided
            description = ""  # Default value if not provided
            person_count = 1  # Default value if not provided
            status = "confirmed" if response == "yes" else "declined" if response == "no" else "pending"
    
            user_updated = db_operations.add_user_to_event(username, event_name, person_count, droid_count, description, status)
            if user_updated == False:
                print(f"Failed to update user {username} with event details.")
    
            # Save the dropdown message's custom_id into the message_ids collection
            db_operations.add_message_id(custom_id, event_name, interaction.channel.id)
    
            # Optionally, send a message to the organizer channel
            organizers_channel = bot.get_channel(organizer_channel_id)
            if organizers_channel:
                await organizers_channel.send(
                    f"📅 **EVENT** >>> **{interaction.user.display_name}** {readable_response} the event: **{event_name}**."
                )

    except Exception as e:
        await interaction.response.send_message(f"An error occurred in on_interaction, event dropdown: {str(e)}", ephemeral=True)
    






















@bot.tree.command(name="create_activity", description="Add a special amenity for an event", nsfw=True)
@app_commands.describe(
    name="Name of the special activity",
    event_name="Name of the event",
    date="Date of the special activity (DD-MM-YYYY)",
    time="Time of the special activity (HH:MM)",
    price="Price of the special activity (optional)",
    address="Address of the special activity (optional)",
    description="Description of the special activity (optional)",
)
@app_commands.autocomplete(event_name=event_suggestions)
async def add_special_amenity(interaction: discord.Interaction, name: str, event_name: str, date: str, time: str, price: float = None, address: str = None, description: str = None):
    try:
            # Validate date format (DD-MM-YYYY)
        try:
            date_obj = datetime.strptime(date, "%d-%m-%Y")
        except ValueError:
            await interaction.response.send_message("Invalid date format. Please use DD-MM-YYYY.", ephemeral=True)
            return
    
        # Validate time format (HH:MM)
        try:
            time_obj = datetime.strptime(time, "%H:%M")
        except ValueError:
            await interaction.response.send_message("Invalid time format. Please use HH:MM.", ephemeral=True)
            return
    
        # Add the special amenity to the DB
        result = db_operations.add_special_amenity(event_name, name, date_obj, time_obj, price, address, description)
        if result:
            await interaction.response.send_message(f"✅ Special activity '{name}' for event '{event_name}' has been added successfully.")
        else:
            await interaction.response.send_message(f"❌ Special activity '{name}' for event '{event_name}' could not be added.")
                                                    
    except Exception as e:
        await interaction.response.send_message(f"❌ An error occurred while adding the special activity: {str(e)}", ephemeral=True)



@bot.tree.command(name="update_activity", description="Update details of an activity for an event", nsfw=True)
@app_commands.autocomplete(activity_name=amenity_suggestions, event_name=event_suggestions)
@app_commands.describe(
    activity_name="Name of the special activity",
    event_name="Name of the event",
    date="Date of the special activity (DD-MM-YYYY)",
    time="Time of the special activity (HH:MM)",
    price="Price of the special activity (optional)",
    address="Address of the special activity (optional)",
    description="Description of the special activity (optional)",
)
async def update_special_amenity(interaction: discord.Interaction, activity_name: str, event_name: str = None, date: str= None, time: str = None, price: float = None, address: str = None, description: str = None):
    try:
        if "(" in activity_name and ")" in activity_name:
            event_name = activity_name.split(" (")[1].rstrip(")").strip()  # Extract the part inside parentheses
            activity_name = activity_name.split(" (")[0].strip()  # Extract the part before '('
        else:
            activity_name = activity_name.strip()
            event_name = "Unknown Event"  # Default if event name is missing
        # Validate date format (DD-MM-YYYY)
        if date is not None:
            try:
                date_obj = datetime.strptime(date, "%d-%m-%Y")
            except ValueError:
                await interaction.response.send_message("Invalid date format. Please use DD-MM-YYYY.", ephemeral=True)
                return
        else:
            date_obj = None

        # Validate time format (HH:MM)
        if time is not None:
            try:
                time_obj = datetime.strptime(time, "%H:%M")
            except ValueError:
                await interaction.response.send_message("Invalid time format. Please use HH:MM.", ephemeral=True)
                return
        else:
            time_obj = None
        print("got here")
        # Update the special amenity in the DB
        result = db_operations.update_special_amenity(event_name, activity_name, date_obj, time_obj, price, address, description)
        if result:
            await interaction.response.send_message(f"✅ Special activity '{activity_name}' has been updated successfully.")
        else:
            await interaction.response.send_message(f"❌ Special activity '{activity_name}' could not be updated.")

    except Exception as e:
        await interaction.response.send_message(f"❌ An error occurred while updating the special activity: {str(e)}", ephemeral=True)



@bot.tree.command(name="get_activity", description="Get details of an activity for an event")
@app_commands.autocomplete(activity_name=amenity_suggestions)
@app_commands.describe(activity_name="Name of the activity")
async def get_special_amenity(interaction: discord.Interaction, activity_name: str):
    try:
        # Parse activity_name for amenity and event names
        if "(" in activity_name and ")" in activity_name:
            amenity_name = activity_name.split(" (")[0].strip()  # Extract the part before '('
            event_name = activity_name.split(" (")[1].rstrip(")").strip()  # Extract the part inside parentheses
        else:
            amenity_name = activity_name.strip()
            event_name = "Unknown Event"  # Default if event name is missing

        # Fetch the special amenity details from the database
        amenity = db_operations.get_amenity(amenity_name)

        if not amenity:
            await interaction.response.send_message(
                "This special activity does not exist. Did you spell it wrong?", ephemeral=True
            )
            return

        # Extract and format details from the amenity object
        amenity_event_name = amenity.get("event_name", "Unknown Event")
        amenity_date = amenity.get("date_time", datetime.now())
        amenity_time = amenity.get("time", datetime.now())

        formatted_date = amenity_date.strftime("%d-%m-%Y")
        formatted_time = amenity_time.strftime("%H:%M")

        amenity_price = amenity.get("price", "No price provided")
        amenity_address = amenity.get("address", "No address provided")
        amenity_description = amenity.get("description", "No description available")

        # Extract participants from the amenity
        confirmed = amenity.get("participants", {}).get("confirmed", [])
        pending = amenity.get("participants", {}).get("pending", [])
        declined = amenity.get("participants", {}).get("declined", [])

        # Format participant lists into readable strings
        confirmed_participants = ", ".join(confirmed) if confirmed else "No confirmed participants yet."
        pending_participants = ", ".join(pending) if pending else "No participants pending."
        declined_participants = ", ".join(declined) if declined else "No declined participants."

        # Create the embed with all the relevant information
        question_embed = discord.Embed(
            title=f"Details of the activity: {amenity_name}",
            description=f"**Event Name:** {amenity_event_name}\n"
                        f"🗓️ **Date:** {formatted_date}\n"
                        f"🕓 **Time:** {formatted_time}\n"
                        f"🏷️ **Price:** €{amenity_price:.2f}\n"
                        f"📍 **Address:** {amenity_address}\n"
                        f"📝 **Description:** {amenity_description}\n\n"
                        f"👥 **Confirmed Participants:** {confirmed_participants}\n"
                        f"⏳ **Pending Participants:** {pending_participants}\n"
                        f"❌ **Declined Participants:** {declined_participants}",
            color=0x4c65f1
        )

        # Send the embed
        await interaction.response.send_message(embed=question_embed)

    except Exception as e:
        await interaction.response.send_message(f"An error occurred in get_activity: {str(e)}", ephemeral=True)





@bot.tree.command(name="register_for_activity", description="Register for a special activity at an event")
@app_commands.autocomplete(activity_name=amenity_suggestions)
@app_commands.describe(
    activity_name="Name of the special activity"
)
async def register_for_special_amenity(interaction: discord.Interaction, activity_name: str):
    try:
        # print(f"Interaction Data: {interaction.data}")

        # Parse activity_name for amenity and event names
        if "(" in activity_name and ")" in activity_name:
            amenity_name = activity_name.split(" (")[0].strip()  # Extract the part before '('
            event_name = activity_name.split(" (")[1].rstrip(")").strip()  # Extract the part inside parentheses
        else:
            amenity_name = activity_name.strip()
            event_name = "Unknown Event"  # Default if event name is missing

        # print(f"Parsed amenity_name: {amenity_name}, event_name: {event_name}")

        # Fetch the special amenity details from the database
        amenity = db_operations.get_amenity(amenity_name)

        if not amenity:
            await interaction.response.send_message(
                "This special activity does not exist. Did you spell it wrong?", ephemeral=True
            )
            return

        # Extract and format details from the amenity object
        amenity_event_name = amenity.get("event_name", "Unknown Event")
        amenity_date = amenity.get("date_time", datetime.now())
        amenity_time = amenity.get("time", datetime.now())

        formatted_date = amenity_date.strftime("%d-%m-%Y")
        formatted_time = amenity_time.strftime("%H:%M")

        amenity_price = amenity.get("price", "No price provided")
        amenity_address = amenity.get("address", "No address provided")
        amenity_description = amenity.get("description", "No description available")

        # print(f"Amenity Details: {amenity}")

        # Pass correct values to the dropdown
        view = dropdown.SpecialAmenityDropdown(event_name=amenity_event_name, amenity_name=amenity_name)

        # Create the embed with all the relevant information
        question_embed = discord.Embed(
            title=f"Will you be attending the activity: {amenity_name}?",
            description=f"**Event Name:** {amenity_event_name}\n"
                        f"🗓️ **Date:** {formatted_date}\n"
                        f"🕓 **Time:** {formatted_time}\n"
                        f"🏷️ **Price:** €{amenity_price:.2f}\n"
                        f"📍 **Address:** {amenity_address}\n"
                        f"📝 **Description:** {amenity_description}",
            color=0x4c65f1
        )

        # Send the embed and view
        await interaction.response.send_message(embed=question_embed, view=view)

    except Exception as e:
        print(f"Error occurred: {e}")
        await interaction.response.send_message(f"An error occurred in register_for_activity: {str(e)}", ephemeral=True)








@bot.tree.command(name='get_event', description='Get information about an event')
@app_commands.autocomplete(event=event_suggestions)
@app_commands.describe(event="The name of the event")
async def get_event(interaction: discord.Interaction, event: str):
    try:
       # No need to await get_event since it's not async
       event_details = db_operations.get_event(event)
       if not event_details:
           await interaction.response.send_message('Event not found')
           return
       
       # Extracting information from the event_details dictionary
       name = event_details['name']
       description = event_details['description']
       
       location = event_details['location']
       venue = location['venue']
       address = location['address']
       address_str = f"{address.get('street', '❌ N/A')}, {address.get('postal_code', '❌ N/A')} - {address['city']}, {address['country']}"
       website = location['website']
       
       # Formatting dates in EU format
       dates = event_details['dates']
       dates_str = "\n".join([f"{date['open_time']} to {date['close_time']} - {date['day']} {format_date_localized(date['date'], 'EN')}" for date in dates])
       
       arrival_time = event_details['attendance_requirements']['arrival_time']
       attendance_note = event_details['attendance_requirements']['note']
       
       organizer = event_details['organizer']['name']
       
       amenities = event_details['amenities']
       amenities_list = "\n".join([
           f"{'✅' if value else '❌'} {key.replace('_', ' ').title()}" 
           for key, value in amenities.items()
       ])
       
       registration_deadline = convert_date_to_eu(event_details['registration_deadline'])
       
       participants = event_details['participants']
   
       # Helper function to get server nickname or fallback to participant name
       def get_server_nickname(participant_name):
           user = db_operations.get_user(participant_name)
           if user:
               return user.get('server_nickname', participant_name)
           else:
               return participant_name  # Return the participant name if not found in the database
   
       # Fetch server nicknames for confirmed participants
       confirmed_participants = participants['confirmed']
       confirmed_names = [get_server_nickname(participant) for participant in confirmed_participants]
       confirmed_display = "\n".join(confirmed_names) if confirmed_names else "None"
   
       # Fetch server nicknames for pending participants
       pending_participants = participants['pending']
       pending_names = [get_server_nickname(participant) for participant in pending_participants]
       pending_display = "\n".join(pending_names) if pending_names else "None"
   
       # Fetch server nicknames for declined participants
       declined_participants = participants['declined']
       declined_names = [get_server_nickname(participant) for participant in declined_participants]
       declined_display = "\n".join(declined_names) if declined_names else "None"
   
       # Creating the embed message with all the event details
       embed = discord.Embed(title=name, description=description)
   
       # Set the event photo as a thumbnail, if available
       photo_url = event_details.get('photo_url')
       file = None
       if photo_url:
               # Prepare the image path
               file_path = f'{image_dir}/{photo_url}'
   
               # Check if the file exists
               if os.path.exists(file_path):
                   with open(file_path, 'rb') as f:
                       file = discord.File(f, filename=f"{photo_url}")  # Upload the file
                       embed.set_thumbnail(url=f"attachment://{file.filename}")  # Set thumbnail as attachment
   
                   # Add the image as an attachment
                   embed.set_thumbnail(url=f"attachment://{file.filename}")
               else:
                   # Set a fallback image if the file does not exist
                   embed.set_thumbnail(url="https://example.com/default-thumbnail.jpg")  # Fallback thumbnail
   
       embed.add_field(name="📍 Location", value=f"{venue}\n{address_str}\n[Visit Website]({website})", inline=False)
       embed.add_field(name="📅 Event Dates", value=dates_str, inline=False)
       embed.add_field(name="⏰ Arrival Time", value=arrival_time, inline=True)
       embed.add_field(name="👨‍💼 Organizer", value=organizer, inline=True)
       embed.add_field(name="📅 Registration Deadline", value=registration_deadline, inline=False)
       embed.add_field(name="🎫 Attendance Requirements", value=attendance_note, inline=False)
       embed.add_field(name="🛠 Amenities", value=amenities_list, inline=False)
       embed.add_field(name="✅ Confirmed", value=confirmed_display, inline=True)
       embed.add_field(name="⏳ Pending", value=pending_display, inline=True)
       embed.add_field(name="❌ Declined", value=declined_display, inline=True)
       
       # Sending the embed with all the event info
       await interaction.response.send_message(embed=embed, file=file)

    except Exception as e:
        await interaction.response.send_message(f"An error occurred in get_event: {str(e)}")





@bot.tree.command(name="create_event", description="Create a new event with optional details", nsfw=True)
@app_commands.autocomplete(name=event_suggestions, photo_url=image_suggestions)
@app_commands.describe(
    name="Event name",
    description="Event description (optional)",
    photo_url="Event photo URL, if no good choice choose placeholder",
    venue="Event venue (name of the location, like Flanders Expo, you can put a link if that is handy) (optional)",
    street="Street address (optional)",
    postal_code="Postal code (optional)",
    city="City",
    country="Country (optional)",
    website="Event website URL (optional)",
    dates="List of event dates in DD-MM-YYYY format, separated by commas",
    open_times="List of opening times corresponding to each date, separated by commas (optional, HH:MM)",
    close_times="List of closing times corresponding to each date, separated by commas (optional, HH:MM)",
    arrival_time="Arrival time for participants (optional, FORMAT: dayname, HH:MM) => dayname in English: capital letter",
    attendance_note="Attendance requirements note (optional)",
    organizer_name="Organizer's name (optional)",
    registration_deadline="Registration deadline (optional, DD-MM-YYYY)",
    public_access="Is it publicly accessible? (optional, true/false)",
    power_outlets="Are power outlets available? (optional, true/false)",
    travel_expenses_covered="Are travel expenses covered? (optional, true/false)",
    free_parking="Is free parking available? (optional, true/false)",
    lunch_provided="Is lunch provided? (optional, true/false)",
    beverages_provided="Are beverages provided? (optional, true/false)",
    storage_available="Is storage available? (optional, true/false)",
    changing_room="Is there a changing room? (optional, true/false)"
)
async def create_event(
    interaction: discord.Interaction,
    name: str,
    dates: str,
    photo_url: str,
    open_times: str = None,
    close_times: str = None,
    description: str = None,
    venue: str = None,
    street: str = None,
    postal_code: str = None,
    city: str = None,
    country: str = None,
    website: str = None,
    arrival_time: str = None,
    attendance_note: str = None,
    organizer_name: str = None,
    registration_deadline: str = None,
    public_access: bool = None,
    power_outlets: bool = None,
    travel_expenses_covered: bool = None,
    free_parking: bool = None,
    lunch_provided: bool = None,
    beverages_provided: bool = None,
    storage_available: bool = None,
    changing_room: bool = None
):
    try:
        # Parse dates, open_times, and close_times into lists
        date_list = dates.split(',')
        open_time_list = open_times.split(',') if open_times else [None] * len(date_list)
        close_time_list = close_times.split(',') if close_times else [None] * len(date_list)

        # Ensure all lists are of the same length
        if len(date_list) != len(open_time_list) or len(date_list) != len(close_time_list):
            await interaction.response.send_message("The number of dates, open times, and close times must match.")
            return

        # Format dates in the event details, and add the "day" field
        event_dates = []
        for i in range(len(date_list)):
            date_str = date_list[i].strip()
            date_obj = datetime.strptime(date_str, "%d-%m-%Y")
            day_name = date_obj.strftime("%A")  # Get the day of the week (e.g., "Saturday")
            event_dates.append({
                "day": day_name,
                "date": date_obj.strftime("%Y-%m-%d"),
                "open_time": open_time_list[i].strip() if open_time_list[i] else None,
                "close_time": close_time_list[i].strip() if close_time_list[i] else None
            })

        # Build the event details
        event_details = {
            "name": name,
            "description": description,
            "location": {
                "venue": venue,
                "address": {
                    "street": street,
                    "postal_code": postal_code,
                    "city": city,
                    "country": country
                },
                "website": website
            },
            "dates": event_dates,
            "attendance_requirements": {
                "arrival_time": arrival_time,
                "note": attendance_note
            },
            "organizer": {
                "name": organizer_name
            },
            "photo_url": photo_url,
            "amenities": {
                "public_access": public_access,
                "power_outlets": power_outlets,
                "travel_expenses_covered": travel_expenses_covered,
                "free_parking": free_parking,
                "lunch_provided": lunch_provided,
                "beverages_provided": beverages_provided,
                "storage_available": storage_available,
                "changing_room": changing_room
            },
            "registration_deadline": datetime.strptime(registration_deadline, "%d-%m-%Y").strftime("%Y-%m-%d") if registration_deadline else None,
            "participants": {
                "confirmed": [],
                "pending": [],
                "declined": []
            }
        }

        # Create event in the database
        event_id = db_operations.create_event(event_details)
        await interaction.response.send_message(f"Event '{name}' created successfully ")
    
    except Exception as e:
        # Catch any exception and send a message to the user
        await interaction.response.send_message(f"An error occurred while creating the event: {str(e)}")




@bot.tree.command(name="update_event", description="Update details for an existing event.", nsfw=True)
@app_commands.autocomplete(name=event_suggestions,photo_url=image_suggestions)
@app_commands.describe(
    name="Name of the event to update",
    description="Updated description of the event",
    photo_url="Updated photo URL for the event",
    venue="Updated event venue",
    street="Street address of the venue",
    postal_code="Postal code of the venue",
    city="City of the venue",
    country="Country of the venue",
    website="Website link for the venue",
    dates="List of event dates in DD-MM-YYYY format, separated by commas",
    open_times="List of opening times corresponding to each date, separated by commas (optional, HH:MM)",
    close_times="List of closing times corresponding to each date, separated by commas (optional, HH:MM)",
    arrival_time="Arrival time for participants (optional, FORMAT: dayname, HH:MM) => dayname in English: capital letter",
    attendance_note="Additional attendance requirements or notes",
    organizer_name="Organizer name",
    public_access="Is the event open to public? (True/False)",
    power_outlets="Are power outlets available? (True/False)",
    travel_expenses_covered="Are travel expenses covered? (True/False)",
    free_parking="Is free parking available? (True/False)",
    lunch_provided="Is lunch provided? (True/False)",
    beverages_provided="Are beverages provided? (True/False)",
    storage_available="Is storage space available? (True/False)",
    changing_room="Is a changing room available? (True/False)",
    registration_deadline="Registration deadline (YYYY-MM-DD)"
)
async def update_event(
    interaction: discord.Interaction,
    name: str,
    photo_url: str = None,
    description: str = None,
    venue: str = None,
    street: str = None,
    postal_code: str = None,
    city: str = None,
    country: str = None,
    website: str = None,
    dates: str = None,
    open_times: str = None,
    close_times: str = None,
    arrival_time: str = None,
    attendance_note: str = None,
    organizer_name: str = None,
    public_access: bool = None,
    power_outlets: bool = None,
    travel_expenses_covered: bool = None,
    free_parking: bool = None,
    lunch_provided: bool = None,
    beverages_provided: bool = None,
    storage_available: bool = None,
    changing_room: bool = None,
    registration_deadline: str = None
):
    try: 
       # Defer response for follow-up
       await interaction.response.defer()
   
       # Initialize the updates dictionary
       updates = {}
       current_event = db_operations.get_event(name)
   
       # Handle updating the description, venue, and location
       if photo_url:
           updates["photo_url"] = photo_url
       if description:
           updates["description"] = description
       if venue:
           updates["location.venue"] = venue

       # take the current location.address info and update with new values
       if current_event and "location" in current_event and "address" in current_event["location"]:
           current_address = current_event["location"]["address"]
           street = street if street else current_address.get("street", "")
           postal_code = postal_code if postal_code else current_address.get("postal_code", "")
           city = city if city else current_address.get("city", "")
           country = country if country else current_address.get("country", "")

       updates["location.address"] = {
                "street": street,
                "postal_code": postal_code,
                "city": city,
                "country": country
            }
       
       if website:
           updates["location.website"] = website
   
       # Handle updating the event dates
       if dates or open_times or close_times:
           # Split date, open_time, and close_time strings into lists
           date_list = dates.split(',') if dates else []
           open_time_list = open_times.split(',') if open_times else [None] * len(date_list)
           close_time_list = close_times.split(',') if close_times else [None] * len(date_list)
   
           # Ensure all lists are of the same length
           if len(date_list) != len(open_time_list) or len(date_list) != len(close_time_list):
               await interaction.followup.send("The number of dates, open times, and close times must match.")
               return
   
           # Format the dates and times, adding the "day" field
           event_dates = []
           for i in range(len(date_list)):
               date_str = date_list[i].strip()
               date_obj = datetime.strptime(date_str, "%d-%m-%Y")
               day_name = date_obj.strftime("%A")
               event_dates.append({
                   "day": day_name,
                   "date": date_obj.strftime("%Y-%m-%d"),
                   "open_time": open_time_list[i].strip() if open_time_list[i] else None,
                   "close_time": close_time_list[i].strip() if close_time_list[i] else None
               })
           
           updates["dates"] = event_dates
   
       # Handle updating the attendance requirements
       if arrival_time:
           updates["attendance_requirements.arrival_time"] = arrival_time
       if attendance_note:
           updates["attendance_requirements.note"] = attendance_note
   
       # Handle updating the organizer information
       if organizer_name:
           updates["organizer.name"] = organizer_name
   
       # Handle updating amenities
       if public_access is not None:
           updates["amenities.public_access"] = public_access
       if power_outlets is not None:
           updates["amenities.power_outlets"] = power_outlets
       if travel_expenses_covered is not None:
           updates["amenities.travel_expenses_covered"] = travel_expenses_covered
       if free_parking is not None:
           updates["amenities.free_parking"] = free_parking
       if lunch_provided is not None:
           updates["amenities.lunch_provided"] = lunch_provided
       if beverages_provided is not None:
           updates["amenities.beverages_provided"] = beverages_provided
       if storage_available is not None:
           updates["amenities.storage_available"] = storage_available
       if changing_room is not None:
           updates["amenities.changing_room"] = changing_room
   
       # Handle updating registration deadline
       if registration_deadline:
           updates["registration_deadline"] = datetime.strptime(registration_deadline, "%Y-%m-%d").strftime("%Y-%m-%d")
   
       # Call the update function (this should be defined in your db_operations)
       success = db_operations.update_event(name, updates)
   
       # Respond to the user
       if success:
           await interaction.followup.send(f"Event '{name}' has been updated successfully.")
       else:
           await interaction.followup.send(f"Event '{name}' could not be updated. Please ensure the event exists.")

    except Exception as e:
        await interaction.response.send_message(f"An error occurred in update_event: {str(e)}")




# Command to delete an existing event
@bot.tree.command(name="delete_event", description="Delete an event by name", nsfw=True)
@app_commands.autocomplete(name=event_suggestions)
@app_commands.describe(name="Event name to delete")
async def delete_event(interaction: discord.Interaction, name: str):
    try:
       success = db_operations.delete_event(name)
       if success:
           await interaction.response.send_message(f"Event '{name}' deleted successfully.")
       else:
           await interaction.response.send_message(f"Event '{name}' not found.")

    except Exception as e:
        await interaction.response.send_message(f"An error occurred in delete_event: {str(e)}")



@bot.tree.command(name="register", description="Register a user to the database.")
async def register_user(interaction: discord.Interaction):
    try: 
       user = interaction.user
       
       # Extract relevant user data
       
       discord_name = f"{user.name}"
       server_nickname = user.display_name if user.display_name else discord_name
       avatar_url = user.display_avatar.url
       roles = [role.name for role in user.roles if role.name not in ["@everyone"]]
   
       # Check if the user is already registered
       existing_user = db_operations.get_user(discord_name)
       if existing_user:
           await interaction.response.send_message(f"❌ You are already registered.")
           return
       
       # Register new user
       db_operations.create_user(discord_name, server_nickname, avatar_url, roles, user)
       await interaction.response.send_message(f"✅ {server_nickname}, you have been registered successfully. You can now register yourself for events!")

    except Exception as e:
        await interaction.response.send_message(f"An error occurred in register_user: {str(e)}")



@bot.tree.command(name="register_for_event", description="Register for an event with details.")
@app_commands.autocomplete(event_name=event_suggestions)
@app_commands.describe(
    event_name="The name of the event you would like to participate in",
    will_attend="Will you come to this event? if yes, please fill out the next 2 optional questions",
    person_count="Number of people you will bring",
    droid_count="Number of droids you will bring",
    description="Please explain what you will be bringing and any other relevant information"
    
)
async def register_for_event(interaction: discord.Interaction, event_name: str, will_attend: bool,person_count: int, droid_count: int, description: str = "", ):
    try: 

       current_user = interaction.user
   
       # Check if the event exists
       event = db_operations.get_event(event_name)
       if not event:
           await interaction.response.send_message(
               f"⚠️ Event {event_name} not found. Please check the event name and try again."
           )
           return
       
       # Check if the user exists
       user = db_operations.get_user(current_user.name)
       if not user:
           await interaction.response.send_message(
               f"⚠️ User {current_user.name} not found. Please register first using **/register**"
           )
           return
   
       if will_attend:
           # Add the user to their own event list
           user_success = db_operations.add_user_to_event(current_user.name, event_name, person_count, droid_count, description,"confirmed")
           
           # Add the user to the event's confirmed participants
           event_success = db_operations.add_participant_to_event(event_name, current_user.name, "confirmed")
           
           if user_success and event_success:
               await interaction.response.send_message(
                   f"✅ You have successfully registered for the event: '{event_name}' with {droid_count} droid(s). for {person_count} person(s)."
               )
           else:
               await interaction.response.send_message(
                   f"❌ You are already registered for the event: '{event_name}' {current_user.mention}"
               )
       else:
           user_success = db_operations.add_user_to_event(current_user.name, event_name, droid_count, description, "declined")
           # Add the user to the event's declined participants
           event_success = db_operations.add_participant_to_event(event_name, current_user.name, "declined")
           
           if event_success:
               await interaction.response.send_message(
                   f"❌ You have declined the invitation to the event: '{event_name}', and your response has been saved."
               )
           else:
               await interaction.response.send_message(
                   f"⚠️ There was an issue saving your response for the event: '{event_name}'. Please try again later."
               )

    except Exception as e:
        await interaction.response.send_message(f"An error occurred in register_for_event: {str(e)}")





@bot.tree.command(name="delete_registration", description="Delete your registration for an event.")
@app_commands.autocomplete(event_name=event_suggestions)
@app_commands.describe(event_name="The name of the event you would like to unregister from")
async def delete_registration(interaction: discord.Interaction, event_name: str):
    try: 
       current_user = interaction.user
   
       # Check if the event exists
       event = db_operations.get_event(event_name)
       if not event:
           await interaction.response.send_message(
               f"⚠️ Event {event_name} not found. Please check the event name and try again."
           )
           return
       
       # Check if the user exists
       user = db_operations.get_user(current_user.name)
       if not user:
           await interaction.response.send_message(
               f"⚠️ User {current_user.name} not found. Please register first using **/register**"
           )
           return
   
       # Check if the user is registered for the event
       registered_events = db_operations.get_registered_events(current_user.name)
       event_registered = False
       for registered_event in registered_events:
           if registered_event['event_name'] == event_name:
               event_registered = True
               break
   
       if not event_registered:
           await interaction.response.send_message(
               f"❌ You are not registered for the event: '{event_name}' {current_user.mention}, please use **/register_for_event** to register."
           )
           return
   
       # Remove user from their own registration and update event participants
       user_success = db_operations.remove_user_from_event(current_user.name, event_name)
       event_success = db_operations.update_participant_status(event_name, current_user.name, "declined")
       
       if user_success and event_success:
           await interaction.response.send_message(
               f"✅ You have successfully unregistered from the event: '{event_name}'. Your status has been updated to 'Declined'."
           )
       else:
           await interaction.response.send_message(
               f"❌ There was an issue updating your registration for the event: '{event_name}' {current_user.mention}"
           )

    except Exception as e:
        await interaction.response.send_message(f"An error occurred in delete_registration: {str(e)}")
   



@bot.tree.command(name="update_registration", description="Update your registration details for an event.")
@app_commands.autocomplete(event_name=event_suggestions)
@app_commands.describe(
    event_name="The name of the event you would like to update",
    droid_count="The updated number of droids you will bring",
    description="The updated description of what you will bring or any changes"
)
async def update_registration(interaction: discord.Interaction, event_name: str, person_count:int, droid_count: int, description: str):
    try: 
       current_user = interaction.user
   
       event = db_operations.get_event(event_name)
       if not event:
           await interaction.response.send_message(
               f"⚠️ Event {event_name} not found. Please check the event name and try again."
           )
           return
   
       # Check if the user exists
       user = db_operations.get_user(current_user.name)
       if not user:
           await interaction.response.send_message(
               f"⚠️ User {current_user.name} not found. Please register first using **/register**"
           )
           return
       
       # Check if the user is already registered for the event
       registered_events = db_operations.get_registered_events(current_user.name)
       event_registered = False
   
       for registered_event in registered_events:
           if registered_event['event_name'] == event_name:
               event_registered = True
               break
   
       if not event_registered:
           await interaction.response.send_message(
               f"❌ You are not registered for the event: '{event_name}' {current_user.mention}, please use **/register_for_event** to register."
           )
           return
   
       # Update user registration for the event
       success = db_operations.update_user_registration(current_user.name, event_name, person_count, droid_count, description)
       if success:
           await interaction.response.send_message(
               f"✅ Your registration for event '{event_name}' has been updated with {droid_count} droid(s). for {person_count} person(s)."
           )
       else:
           await interaction.response.send_message(
               f"❌ There was an issue updating your registration for the event: '{event_name}' {current_user.mention}"
           )

    except Exception as e:
        await interaction.response.send_message(f"An error occurred in update_registration: {str(e)}")

    

@bot.tree.command(name='get_events_by_user', description="Show a registered user's event participation status")
@app_commands.autocomplete(user=user_suggestions)
@app_commands.describe(user="The user whose status you want to view")
async def user_event_status(interaction: discord.Interaction, user: str):
    try: 
       # Extract the Discord name from the input format: "Nickname (DiscordName)"
       match = re.search(r'\(([^)]+)\)', user)
       if not match:
           await interaction.response.send_message(
               f"⚠️ Unable to get the Discord name from input '{user}'. Please select your name from the options, if not there first use **/register**."
           )
           return
       discord_name = match.group(1)  # Get the text inside the parentheses
   
       # Fetch the user data from the database using the extracted Discord name
       user_data = db_operations.get_user(discord_name)
       if not user_data:
           await interaction.response.send_message(
               f"⚠️ User '{discord_name}' not found in the database. Please register first using **/register**."
           )
           return
   
       # Extract user details
       server_nickname = user_data.get("server_nickname", discord_name)
       avatar_url = user_data.get("avatar_url", None)
   
       # Extract events the user has registered for (from the user's "events" field)
       events = user_data.get("events", [])
   
       # Fetch event participation statuses
       confirmed_events = []
       declined_events = []
       pending_events = []
   
       # Loop through the user's events and check the status of each one
       for event_entry in events:
           event_name = event_entry.get("event_name")
           event_status = event_entry.get("status")  # Assuming the status field is already there
           
           if event_status == "confirmed":
               confirmed_events.append(event_name)
           elif event_status == "declined":
               declined_events.append(event_name)
           elif event_status == "pending":
               pending_events.append(event_name)
   
       # Format confirmed events
       confirmed_display = "\n".join(confirmed_events) if confirmed_events else "None"
   
       # Format declined events
       declined_display = "\n".join(declined_events) if declined_events else "None"
   
       # Format pending events
       pending_display = "\n".join(pending_events) if pending_events else "None"
   
       # Create an embed message
       embed = discord.Embed(
           title=f"Event Status for {server_nickname}",
           description=f"Here you can see all the events that {server_nickname} is going to or has declined.",
           color=0x4c65f1
       )
       if avatar_url:
           embed.set_thumbnail(url=avatar_url)
       embed.add_field(name="✅ Events Attending", value=confirmed_display, inline=False)
       embed.add_field(name="❌ Events Declined", value=declined_display, inline=False)
       embed.add_field(name="⏳ Events Pending", value=pending_display, inline=False)
       embed.set_footer(text=f"Showing events for user: {discord_name}")
   
       # Send the embed
       await interaction.response.send_message(embed=embed)

    except Exception as e:
        await interaction.response.send_message(f"An error occurred in get_events_by_user: {str(e)}")







@bot.tree.command(name='add_non_discord_user', description="Add a new non-Discord user to the database", nsfw=True)
@app_commands.describe(name="The unique name of the user (e.g., email or other identifier)", email="The full name of the user")
@app_commands.checks.has_any_role(admin)
async def add_non_discord_user(interaction: discord.Interaction, name: str, email: str):
    try: 
       # Add the non-Discord user to the database
       success = db_operations.add_non_discord_user(name, email)
       
       if success:
           await interaction.response.send_message(f"✅ Non-Discord user '{name}' with email '{email}' has been added successfully.")
       else:
           await interaction.response.send_message(f"❌ User '{name}' already exists in the database.")
    
    except Exception as e:
        await interaction.response.send_message(f"An error occurred in add_non_discord_user: {str(e)}")


@add_non_discord_user.error
async def add_non_discord_user_error(interaction: discord.Interaction, error: Exception):
    if "You are missing at least one of the required roles:" in str(error):
        await interaction.response.send_message("🚫 You do not have permission to add non-Discord users.")


@bot.tree.command(name='update_event_non_discord', description="Update/add the event participation status for a non-Discord user", nsfw=True)
@app_commands.describe(identifier="Name or email of the non-Discord user", event_name="Name of the event", status="Event status: 'confirmed' or 'declined'")
@app_commands.autocomplete(identifier=non_discord_suggestions)
@app_commands.autocomplete(status=status_suggestions, event_name=event_suggestions)
@app_commands.checks.has_any_role(admin)
async def update_event_status_non_discord(interaction: discord.Interaction, identifier: str, event_name: str, status: str):
    try: 
       # Validate status
       if status not in ["confirmed", "declined"]:
           await interaction.response.send_message("⚠️ Invalid status. Please use 'confirmed' or 'declined'.")
           return
   
       # Update the event status for the non-Discord user and event participants
       db_operations.update_event_status_for_non_discord_user(identifier, event_name, status)
       await interaction.response.send_message(f"✅ Updated event status for non-Discord user '{identifier}' to '{status}' for event '{event_name}'.")
   
    except Exception as e:
         await interaction.response.send_message(f"An error occurred in update_event_status_non_discord: {str(e)}")

@update_event_status_non_discord.error
async def update_event_status_non_discord_error(interaction: discord.Interaction, error: Exception):
    if "You are missing at least one of the required roles:" in str(error):
        await interaction.response.send_message("🚫 You do not have permission to add non-Discord users.")


@bot.tree.command(name='remove_event_non_discord', description="Remove a non-Discord user's participation in an event", nsfw=True)
@app_commands.autocomplete(identifier=non_discord_suggestions, event_name=event_suggestions)
@app_commands.describe(identifier="Name or email of the non-Discord user", event_name="Name of the event")
@app_commands.checks.has_any_role(admin)
async def remove_event_non_discord(interaction: discord.Interaction, identifier: str, event_name: str):
    try: 
       # Remove the non-Discord user from the event and update the event participants list
       db_operations.remove_event_for_non_discord_user(identifier, event_name)
       await interaction.response.send_message(f"✅ Removed non-Discord user '{identifier}' from event '{event_name}'.")
    
    except Exception as e:
        await interaction.response.send_message(f"An error occurred in remove_event_non_discord: {str(e)}")

@remove_event_non_discord.error
async def remove_event_non_discord_error(interaction: discord.Interaction, error: Exception):
    if "You are missing at least one of the required roles:" in str(error):
        await interaction.response.send_message("🚫 You do not have permission to add non-Discord users.")




@bot.tree.command(name="create_event_channel", description="Create a new channel for an event", nsfw=True)
@app_commands.autocomplete(event_name=event_suggestions)
@app_commands.describe(
    event_name="Name of the event",
    is_cancelled="Whether the event is cancelled (true/false)"
)
async def create_event_channel(
        interaction: discord.Interaction,
        event_name: str,
        is_cancelled: bool
):
    global events_category_id
    try:
        # Fetch event details from the database
        event = db_operations.get_event(event_name)

        if not event:
            await interaction.response.send_message(
                f"No event found matching '{event_name}'. Please check the name and try again.", ephemeral=True
            )
            return

        # Extract necessary details from the event
        event_name = event["name"]
        event_dates = event["dates"]
        # year = event_dates[0]["date"].split("-")[0]  # Extract the year from the first date

        # Format the dates into a single string (e.g., "1 2 November")
        formatted_dates = " ".join([
            f'{int(date["date"].split("-")[2])} {datetime.strptime(date["date"].split("-")[1], "%m").strftime("%B").lower()}'
            for date in event_dates
        ])

        # Determine the status emoji
        status_emoji = "❌" if is_cancelled else "✅"

        # Format the channel name
        channel_name = f"{status_emoji} {event_name} {formatted_dates}".replace(" ", "-").lower()

        # Fetch the category by ID
        category = discord.utils.get(interaction.guild.categories, id=events_category_id)
        if not category:
            await interaction.response.send_message(
                f"Category with ID '{events_category_id}' not found. Please check the ID.", ephemeral=True
            )
            return

                # Retrieve the role that should have access to archived channels
        member_role = discord.utils.get(interaction.guild.roles, name="member")
        events_role = discord.utils.get(interaction.guild.roles, name="Events")

        if not member_role or not events_role:
            await interaction.response.send_message(
                "Role 'member or Events' not found. Please ensure the role exists.", ephemeral=True
            )
            return

        # Define the permission overwrites for the archived channel
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),  # Deny access to @everyone
            member_role: discord.PermissionOverwrite(view_channel=True),  # Allow access for members
            events_role: discord.PermissionOverwrite(view_channel=True) # Allow access for events
        }

        new_channel = await category.create_text_channel(name=channel_name, overwrites=overwrites)

        # Store the channel ID in the database
        db_operations.store_channel_id(event_name, new_channel.id)

        await interaction.response.send_message(
            f"✅ Channel '{new_channel.name}' has been created under the category '{category.name}'.",
            ephemeral=True
        )

    except Exception as e:
        await interaction.response.send_message(
            f"❌ An error occurred while creating the channel: {str(e)}", ephemeral=True
        )



@bot.tree.command(name="update_event_channel", description="Update the name of an event channel", nsfw=True)
@app_commands.autocomplete(event_name=event_suggestions)
@app_commands.describe(
    event_name="Name of the event to update",
    is_cancelled="Whether the event is cancelled (true/false)"
)
async def update_event_channel(
        interaction: discord.Interaction,
        event_name: str,
        is_cancelled: bool
):
    global events_category_id
    try:
        # Fetch event details from the database
        event = db_operations.get_event(event_name)

        if not event:
            await interaction.response.send_message(
                f"No event found matching '{event_name}'. Please check the name and try again.", ephemeral=True
            )
            return

        # Retrieve the channel ID from the database
        channel_id = db_operations.get_channel_id(event_name)
        if not channel_id:
            await interaction.response.send_message(
                f"No channel found for the event '{event_name}'.", ephemeral=True
            )
            return

        # Get the channel
        channel = interaction.guild.get_channel(channel_id)
        if not channel:
            await interaction.response.send_message(
                f"Channel with ID '{channel_id}' not found in the server.", ephemeral=True
            )
            return

        # Format the new channel name
        event_dates = event["dates"]
        formatted_dates = " ".join([
            f'{int(date["date"].split("-")[2])} {datetime.strptime(date["date"].split("-")[1], "%m").strftime("%B").lower()}'
            for date in event_dates
        ])
        status_emoji = "❌" if is_cancelled else "✅"
        new_channel_name = f"{status_emoji} {event_name} {formatted_dates}".replace(" ", "-").lower()

        # Update the channel name
        await channel.edit(name=new_channel_name)

        await interaction.response.send_message(
            f"✅ Channel name updated to '{new_channel_name}'.", ephemeral=True
        )

    except Exception as e:
        await interaction.response.send_message(
            f"❌ An error occurred while updating the channel: {str(e)}", ephemeral=True
        )



@bot.tree.command(name="archive_event_channel", description="Move an event channel to the archive", nsfw=True)
@app_commands.autocomplete(event_name=event_suggestions)
@app_commands.describe(event_name="Name of the event")
async def archive_event_channel(interaction: discord.Interaction, event_name: str):
    global archive_category_id
    global event_organizer_id
    try:
        # Fetch the event channel ID from the database
        channel_id = db_operations.get_channel_id(event_name)  # Expecting an integer directly
        if not channel_id:
            await interaction.response.send_message(
                f"No channel found for the event '{event_name}'. Please check the event name and try again.", ephemeral=True
            )
            return

        # Retrieve the channel object
        channel = interaction.guild.get_channel(channel_id)
        if not channel:
            await interaction.response.send_message(
                f"Channel with ID '{channel_id}' not found. Please ensure the channel exists.", ephemeral=True
            )
            return

        # Get the archive category
        archive_category = discord.utils.get(interaction.guild.categories, id=archive_category_id)
        if not archive_category:
            await interaction.response.send_message(
                f"Category with ID '{archive_category_id}' not found. Please check the ID.", ephemeral=True
            )
            return

        # Retrieve the role that should have access to archived channels
        archive_manager_role = discord.utils.get(interaction.guild.roles, name="Event Organizer")  # Replace with role name
        if not archive_manager_role:
            await interaction.response.send_message(
                "Role 'Event Organizer' not found. Please ensure the role exists.", ephemeral=True
            )
            return

        # Define the permission overwrites for the archived channel
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),  # Deny access to @everyone
            archive_manager_role: discord.PermissionOverwrite(view_channel=True)  # Allow access for Event Organizer
        }

        # Move the channel to the archive category and apply the permission overwrites
        await channel.edit(category=archive_category, overwrites=overwrites)

        await interaction.response.send_message(
            f"✅ Channel '{channel.name}' has been moved to the archive category and permissions have been updated.",
            ephemeral=True
        )

    except Exception as e:
        await interaction.response.send_message(
            f"❌ An error occurred while archiving the channel: {str(e)}", ephemeral=True
        )




@bot.tree.command(name="export_event_data", description="Export event data as an Excel file", nsfw=True)
@app_commands.describe(event_name="Name of the event to export data for")
@app_commands.autocomplete(event_name=event_suggestions)
async def export_event_data(interaction: discord.Interaction, event_name: str):
    try:
        # Fetch event data from the database
        event = db_operations.get_event(event_name)
        if not event:
            await interaction.response.send_message(
                f"No event found matching '{event_name}'. Please check the name and try again.", ephemeral=True
            )
            return

        # Create a new Excel workbook and sheet
        wb = openpyxl.Workbook()
        sheet = wb.active
        sheet.title = f"{event_name} Data"

        # Write event data to the first rows
        sheet.append(["Field", "Value"])
        sheet.append(["Event Name", event.get("name", "N/A")])
        sheet.append(["Description", event.get("description", "N/A")])

        # Add event dates
        sheet.append(["Dates", ", ".join([
            f'{date["day"]} ({date["date"]}) {date["open_time"]}-{date["close_time"]}'
            for date in event.get("dates", [])
        ])])

        # Add location details
        location = event.get("location", {})
        address = location.get("address", {})
        sheet.append(["Venue", location.get("venue", "N/A")])
        sheet.append(["Address", f'{address.get("street", "")}, {address.get("postal_code", "")}, {address.get("city", "")}, {address.get("country", "")}'])

        # Add amenities and other fields
        amenities = event.get("amenities", {})
        sheet.append(["Public Access", amenities.get("public_access", "No")])
        sheet.append(["Power Outlets", amenities.get("power_outlets", "No")])
        sheet.append(["Free Parking", amenities.get("free_parking", "No")])

        # Fetch user data for confirmed participants
        participants = event.get("participants", {})
        confirmed_users = participants.get("confirmed", [])

        # Write user data in a new section
        sheet.append([])  # Empty row to separate event data from user data
        sheet.append(["User Name", "Email", "Discord Name", "Person Count", "Droid Count"])
        
        for user_name in confirmed_users:
            # First try to fetch from get_user
            user_data = db_operations.get_user(user_name)

            if user_data:
                discord_name = user_data.get("server_nickname", "N/A")
                email = user_data.get("email", "N/A")
                # Find event registration details for the user
                event_registration = next((event for event in user_data.get("events", []) if event["event_name"] == event_name), None)
                person_count = event_registration["person_count"] if event_registration else "N/A"
                droid_count = event_registration["droid_count"] if event_registration else "N/A"
                sheet.append([user_name, email, discord_name, person_count, droid_count])
            else:
                # If not found, try the non-discord users collection
                non_discord_user_data = db_operations.get_user_from_non_discord_users(user_name)
                if non_discord_user_data:
                    # Only store the name for non-Discord users
                    sheet.append([user_name, "N/A", "N/A", "N/A", "N/A"])

        # Save the Excel file to a BytesIO object
        excel_file = io.BytesIO()
        wb.save(excel_file)
        excel_file.seek(0)

        # Send the file as a Discord file
        file = discord.File(fp=excel_file, filename=f"{event_name.replace(' ', '_').lower()}_data.xlsx")

        # Send the file in the interaction response
        await interaction.response.send_message(
            content=f"📁 Here is the Excel export for '{event_name}':",
            file=file
        )

    except Exception as e:
        await interaction.response.send_message(
            f"❌ An error occurred while exporting the event data: {str(e)}", ephemeral=True
        )

bot.run(os.getenv('token'))