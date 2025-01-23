from discord.ui import View, Select
import discord

class EventResponseDropdown(View):
    def __init__(self, event_name: str):
        super().__init__(timeout=None)  # No timeout ensures persistence
        self.event_name = event_name

        # Add a dropdown menu
        self.add_item(Select(
            placeholder="Will you be attending this event?",
            custom_id=f"event_response_{event_name}",  # Unique ID for persistence
            options=[
                discord.SelectOption(label="Yes", value="yes", emoji="✅", description="I will be attending this event"),
                discord.SelectOption(label="Not sure yet", value="not_sure", emoji="❔", description="I am unsure about attending this event"),
                discord.SelectOption(label="No", value="no", emoji="❌", description="I will not be attending this event")
            ]
        ))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        # Allow all users to interact
        return True


class SpecialAmenityDropdown(View):
    def __init__(self, event_name: str, amenity_name: str):
        super().__init__(timeout=None)
        self.event_name = event_name
        self.amenity_name = amenity_name

        # Create options for the dropdown
        options = [
            discord.SelectOption(label="Yes", value="yes", emoji="✅", description="I will attend"),
            discord.SelectOption(label="Not Sure", value="not_sure", emoji="❔", description="I am unsure"),
            discord.SelectOption(label="No", value="no", emoji="❌", description="I will not attend")
        ]

        # Add the dropdown menu for this specific amenity
        self.add_item(Select(
            placeholder=f"Will you be attending this activity?",
            custom_id=f"special_amenity_response_{event_name}_{amenity_name}",
            options=options
        ))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return True

