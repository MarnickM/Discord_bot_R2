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
from pymongo import MongoClient
import re

load_dotenv()



class DatabaseConnection:
    def __init__(self):
        self.connection_string = os.getenv("mongoDB_url")
        self.client = MongoClient(self.connection_string)
        self.db = self.client['R2Builders']
        self.collection = self.db['Events']
        self.users_collection = self.db['Users']
        self.droids_collection = self.db['Droids']
        self.non_discord_users_collection = self.db['Non-discord-users']
        self.message_ids_collection = self.db['message_ids']
        self.special_amenities_collection = self.db['special-amenities']
        self.event_channel_collection = self.db['event-channels']

    
    # User Operations
    def get_user(self, discord_name):
        """Fetch a user by discord name"""
        return self.users_collection.find_one({"discord_name": discord_name})
    
    def get_user_from_non_discord_users(self, name):
       """Fetch a non-Discord user by name, allowing for partial matches"""
       # Use regex for case-insensitive partial matching
       regex = re.compile(name, re.IGNORECASE)
       return self.non_discord_users_collection.find({"name": regex})
    
    def get_users(self, search_string: str):
        query = {"server_nickname": {"$regex": search_string, "$options": "i"}} 
        return [f"{user['server_nickname']} ({user['discord_name']})" for user in self.users_collection.find(query).limit(25)]
    
    def create_user(self, discord_name, server_nickname, avatar_url, roles, user_object):
         """Create a new user in the Users collection"""
         # Extract the relevant attributes from the discord.Member object
         user_object_data = {
             "id": user_object.id,  # Discord user ID
             "name": user_object.name,
             "discriminator": user_object.discriminator,
             "nick": user_object.nick,
             "guild_id": user_object.guild.id
         }
         
         user_data = {
             "discord_name": discord_name,
             "server_nickname": server_nickname,
             "avatar_url": avatar_url,
             "roles": roles,
             "registered": False,
             "user_object": user_object_data,  # Save the simplified user object
             "events": []
         }
         result = self.users_collection.insert_one(user_data)
         return result.inserted_id

    def update_user_roles(self, discord_name, roles):
        """Update the user's roles"""
        result = self.users_collection.update_one(
            {"discord_name": discord_name},
            {"$set": {"roles": roles}}
        )
        return result.modified_count > 0

    def add_user_to_event(self, discord_name, event_name, person_count, droid_count, description, status):
        """Add a user to an event with additional information, or update the status if they are already part of it."""
        
        event_entry = {
            "person_count": person_count,
            "droid_count": droid_count,
            "description": description,
            "status": status
        }
    
        # Try to update the existing event if it exists, otherwise add a new event entry
        result = self.users_collection.update_one(
            {"discord_name": discord_name, "events.event_name": event_name},
            {"$set": {f"events.$.status": status, f"events.$.person_count": person_count, f"events.$.droid_count": droid_count, f"events.$.description": description}},
            upsert=False  # Don't insert a new document if no match is found
        )
    
        if result.modified_count == 0:
            # If no event was updated, insert a new event entry
            result = self.users_collection.update_one(
                {"discord_name": discord_name},
                {"$push": {"events": {**event_entry, "event_name": event_name}}}
            )
    
        return result.modified_count > 0

    

    def add_participant_to_event(self, event_name, participant_name, status):
        """
        Add a participant to the confirmed, declined, or pending list of an event.
        :param event_name: The name of the event
        :param participant_name: The name of the participant
        :param status: Either 'confirmed', 'declined', or 'pending'
        :return: True if the operation is successful, False otherwise
        """
        event = self.collection.find_one({"name": event_name})
        if not event:
            return False
    
        if status not in ["confirmed", "declined", "pending"]:
            return False
    
        # Check if the participant is in any other status, and remove them from that category if necessary
        for category in ["confirmed", "declined", "pending"]:
            if category != status and participant_name in event["participants"][category]:
                # Remove from the other categories
                self.collection.update_one(
                    {"name": event_name},
                    {"$pull": {f"participants.{category}": participant_name}}
                )
    
        # Now add the participant to the new status
        # Avoid duplicate entries in the selected status
        if participant_name not in event["participants"][status]:
            self.collection.update_one(
                {"name": event_name},
                {"$addToSet": {f"participants.{status}": participant_name}}
            )
            return True
    
        return False
    


    def get_events(self, search_string: str):
        query = {"name": {"$regex": search_string, "$options": "i"}}
        return [event['name'] for event in self.collection.find(query).limit(25)]
    
    def get_event(self, search_string: str):
        query = {"name": search_string}
        return self.collection.find_one(query)
    
    def create_event(self, event_details):
        result = self.collection.insert_one(event_details)
        return result.inserted_id

    def update_event(self, event_name, updates):
        result = self.collection.update_one(
            {"name": event_name},
            {"$set": updates}
        )
        return result.modified_count > 0
    
    def delete_event(self, event_name):
        result = self.collection.delete_one({"name": event_name})
        return result.deleted_count > 0
    
    def get_droids(self, search_string: str):
        query = {"name": {"$regex": search_string, "$options": "i"}}
        return [droid['name'] for droid in self.droids_collection.find(query).limit(25)]
    
    def get_registered_events(self, discord_name):
        user = self.users_collection.find_one({"discord_name": discord_name})
        if user and 'events' in user:
            return user['events']  # Return the full event objects, not just event names
        return []

    def remove_user_from_event(self, user_name, event_name):
         # Find user and remove the event from the list
         user = self.users_collection.find_one({"discord_name": user_name})
         if user:
             # Find the event dictionary in the events list
             event_to_remove = next((event for event in user.get('events', []) if event['event_name'] == event_name), None)
             if event_to_remove:
                 self.users_collection.update_one(
                     {"discord_name": user_name},
                     {"$pull": {"events": event_to_remove}}  # Remove the specific event dictionary from the user's events list
                 )
                 return True
         return False



    def update_participant_status(self, event_name, user_name, status):
        # Find the event
        event = self.collection.find_one({"name": event_name})
        if not event:
            return False
    
        # Update confirmed/declined participants
        if status == "declined":
            # Remove from confirmed
            self.collection.update_one(
                {"name": event_name},
                {"$pull": {"participants.confirmed": user_name}}
            )
            # Add to declined if not already there
            self.collection.update_one(
                {"name": event_name},
                {"$addToSet": {"participants.declined": user_name}}
            )
        elif status == "confirmed":
            # Remove from declined
            self.collection.update_one(
                {"name": event_name},
                {"$pull": {"participants.declined": user_name}}
            )
            # Add to confirmed if not already there
            self.collection.update_one(
                {"name": event_name},
                {"$addToSet": {"participants.confirmed": user_name}}
            )
        return True



    def update_user_registration(self, user_name, event_name, person_count, droid_count, description):
        # Find user and update the registration details for the event
        user = self.users_collection.find_one({"discord_name": user_name})
        if user:
            # Iterate through the events to find the matching event
            for event in user.get('events', []):
                if event['event_name'] == event_name:
                    event['person_count'] = person_count
                    # Update the event's droid_count and description
                    event['droid_count'] = droid_count
                    event['description'] = description
    
                    # Update the user's event list in the database
                    result = self.users_collection.update_one(
                        {"discord_name": user_name},  # Find the user by discord_name
                        {"$set": {"events": user['events']}}  # Set the updated events list
                    )
    
                    # Check if the update was successful
                    if result.modified_count > 0:
                        return True
                    else:
                        return False
        return False


    def add_non_discord_user(self, name, email):
        # Ensure the user doesn't already exist in the collection
        existing_user = self.non_discord_users_collection.find_one({"name": name})
        if existing_user:
            return False  # User already exists
        
        # Add new non-Discord user
        user_data = {
            "name": name,
            "email": email,
            "events": []
        }
        
        self.non_discord_users_collection.insert_one(user_data)
        return True

    
    def get_non_discord_users(self, search_string: str):
        query = {"name": {"$regex": search_string, "$options": "i"}}
        return [user['name'] for user in self.non_discord_users_collection.find(query).limit(25)]


    def get_non_discord_user(self, identifier):
        # identifier can be either name or email
        return self.non_discord_users_collection.find_one({"$or": [{"name": identifier}, {"email": identifier}]})
    

    def update_event_status_for_non_discord_user(self, identifier, event_name, status):
        # Get the non-Discord user from the database
        user = self.get_non_discord_user(identifier)
        if user:
            event = next((e for e in user["events"] if e["event_name"] == event_name), None)
            
            # Update event status or add new event if not found
            if event:
                event["status"] = status
            else:
                user["events"].append({"event_name": event_name, "status": status})
            
            # Update non-Discord user's data in the collection
            self.non_discord_users_collection.update_one(
                {"_id": user["_id"]},
                {"$set": {"events": user["events"]}}
            )
            
            # Update the event participants list
            event_details = self.get_event(event_name)  # Fetch event details
            if not event_details:
                return
    
            participants = event_details.get("participants", {"confirmed": [], "declined": []})
            # Add or remove from the correct participants list
            if status == "confirmed":
                if identifier not in participants["confirmed"]:
                    participants["confirmed"].append(identifier)
                if identifier in participants["declined"]:
                    participants["declined"].remove(identifier)
            elif status == "declined":
                if identifier not in participants["declined"]:
                    participants["declined"].append(identifier)
                if identifier in participants["confirmed"]:
                    participants["confirmed"].remove(identifier)
    
            # Update the event participants in the database
            result = self.collection.update_one(
                {"name": event_name},
                {"$set": {"participants": participants}}
            )


    def remove_event_for_non_discord_user(self, identifier, event_name):
        # Get the non-Discord user from the database
        user = self.get_non_discord_user(identifier)
        if user:
            # Remove the event from the user's list
            user["events"] = [e for e in user["events"] if e["event_name"] != event_name]
            
            # Update the non-Discord user's data in the collection
            self.non_discord_users_collection.update_one(
                {"_id": user["_id"]},
                {"$set": {"events": user["events"]}}
            )
    
            # Update the event participants list
            event_details = self.get_event(event_name)  # Fetch event details
            if not event_details:
                return
    
            participants = event_details.get("participants", {"confirmed": [], "declined": []})
    
            # Remove the user from both confirmed and declined lists
            if identifier in participants["confirmed"]:
                participants["confirmed"].remove(identifier)
            if identifier in participants["declined"]:
                participants["declined"].remove(identifier)
    
            # Update the event participants in the database
            self.collection.update_one(
                {"event_name": event_name},
                {"$set": {"participants": participants}}
            )

    def add_message_id(self, custom_id, event_name, channel_id):
        """Store the custom_id with associated event name and channel_id in the message_ids collection."""
        message_data = {
            "custom_id": custom_id,
            "event_name": event_name,
            "channel_id": channel_id
        }
        # Insert the message data into the collection
        result = self.message_ids_collection.insert_one(message_data)
        return result.inserted_id  # Return the inserted ID for confirmation

    def add_special_amenity(self, event_name, name, date, time, price=None, address= None, description=None):
        """Add a special amenity to an event."""
        amenity = {
            "event_name": event_name,
            "name": name,
            "date_time": date,
            "time": time,
            "price": price if price is not None else None,
            "address": address if address is not None else "",
            "description": description if description is not None else "",
            "participants": {
                "confirmed": [],
                "pending": [],
                "declined": []
            }
        }
        result = self.special_amenities_collection.insert_one(amenity)
        return result.inserted_id
    

    def update_special_amenity(self, event_name, name, date=None, time=None, price=None, address=None, description=None):
         """Update a special amenity for an event."""
         # Build the update dictionary dynamically with only non-None fields
         update_fields = {}
         if date is not None:
             update_fields["date_time"] = date
         if time is not None:
             update_fields["time"] = time
         if price is not None:
             update_fields["price"] = price
         if address is not None:
             update_fields["address"] = address
         if description is not None:
             update_fields["description"] = description
     
         if not update_fields:
             raise ValueError("No fields to update were provided.")
     
         # Perform the update operation
         result = self.special_amenities_collection.update_one(
             {"event_name": event_name, "name": name},  # Match criteria
             {"$set": update_fields}  # Update fields
         )
     
         # Return the number of documents modified
         return result.modified_count > 0

        


    def add_user_to_amenity(self, discord_name, event_name, amenity_name, status):
        """Add a user to a special amenity in a specific status category (confirmed, pending, or declined)."""
        
        # Ensure the response is valid
        if status not in ["yes", "not_sure", "no"]:
            return False
        
        amenity = self.special_amenities_collection.find_one({"event_name": event_name, "name": amenity_name})
        if not amenity:
            return False
        
        # Determine the category based on the user's response
        status_mapping = {
            "yes": "confirmed",
            "not_sure": "pending",
            "no": "declined"
        }
        status_category = status_mapping[status]
        
        # Remove the user from all categories they might already be in
        for category in ["confirmed", "pending", "declined"]:
            if discord_name in amenity.get('participants', {}).get(category, []):
                self.special_amenities_collection.update_one(
                    {"event_name": event_name, "name": amenity_name},
                    {"$pull": {f"participants.{category}": discord_name}}  # Remove from the existing category
                )
        
        # Ensure the user is not already in the selected category
        if discord_name not in amenity.get('participants', {}).get(status_category, []):
            # Add the user to the selected category
            self.special_amenities_collection.update_one(
                {"event_name": event_name, "name": amenity_name},
                {"$addToSet": {f"participants.{status_category}": discord_name}}
            )
            return True
        return False


    
    def get_amenity(self, amenity):
        return self.special_amenities_collection.find_one({"name": amenity})
    

    def get_amenities(self, search_string: str):
        query = {"name": {"$regex": search_string, "$options": "i"}}
        return [f"{amenity['name']} ({amenity['event_name']})" for amenity in self.special_amenities_collection.find(query).limit(25)]


    def store_channel_id(self, event_name, channel_id):
        """Store or update the channel ID for a specific event."""
        result = self.event_channel_collection.update_one(
            {"event_name": event_name},  # Filter by event name
            {"$set": {"channel_id": channel_id}},  # Update or set the channel ID
            upsert=True  # Create a new document if it doesn't exist
        )
        return result.upserted_id or channel_id

    
    def get_channel_id(self, event_name):
        """Retrieve the channel ID for a specific event."""
        channel_data = self.event_channel_collection.find_one({"event_name": event_name})
        if channel_data:
            return channel_data["channel_id"]
        return None

    
    # def add_pending(self):
    #     events = self.collection.find()
    #     for event in events:
    #         if "participants" in event:
    #             if "pending" not in event["participants"]:
    #                 # Add the pending category as an empty list if it doesn't exist
    #                 event["participants"]["pending"] = []
    #                 self.collection.update_one(
    #                     {"_id": event["_id"]},
    #                     {"$set": {"participants.pending": []}}
    #                 )
    #                 print(f"Updated event: {event['name']}")
    #             else:
    #                 print(f"Event '{event['name']}' already has a 'pending' category.")
    #         else:
    #             # If participants section doesn't exist, create it with all categories
    #             participants_structure = {
    #                 "confirmed": [],
    #                 "pending": [],
    #                 "declined": []
    #             }
    #             self.collection.update_one(
    #                 {"_id": event["_id"]},
    #                 {"$set": {"participants": participants_structure}}
    #             )
    #             print(f"Added 'participants' section to event: {event['name']}")

    





# async def test_database():
#     db_connection = DatabaseConnection()
#     # Test get_event
#     event = db_connection.add_pending()

# # Run the test
# asyncio.run(test_database())


