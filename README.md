# Astromech Bot

This repository contains a bot designed to help users manage event registrations, activities, and participation details. Below is a comprehensive guide to all the available commands and how to use them.
There are 2 guides, one for regular users and one for admin users.

# 1. Bot Commands Regular User Guide

---

## Table of Contents
1. [Command: `/register`](#command-register)
2. [Command: `/get_event`](#command-get_event)
3. [Command: `/get_events_by_user`](#command-get_events_by_user)
4. [Command: `/get_activity`](#command-get_activity)
5. [Command: `/register_for_event`](#command-register_for_event)
6. [Command: `/register_for_activity`](#command-register_for_activity)
7. [Command: `/update_registration`](#command-update_registration)
8. [Command: `/delete_registration`](#command-delete_registration)

---

## Command: `/register`
**Description**:  
Register a new user in the system’s database.

**How to Use**:  
Type `/register` to add your details to the system. This command is necessary to start participating in events and activities.

**Example**:  
```
/register
```
**Bot Response**:  
- If successful: "You have been successfully registered."
- If unsuccessful: "Registration failed. Please try again."

---

## Command: `/get_event`
**Description**:  
View detailed information about a specific event, including location, dates, times, and participants.

**How to Use**:  
Type `/get_event` and provide the event name when prompted.

**Example**:  
```
/get_event event:Facts Fall 2025
```
**Bot Response**:  
Displays all details about the event "Facts Fall 2025".

---

## Command: `/get_events_by_user`
**Description**:  
Check the event participation status of a registered user, including which events they have confirmed, declined, or are awaiting confirmation.

**How to Use**:  
Type `/get_events_by_user` and provide the user’s name when prompted.

**Example**:  
```
/get_events_by_user user:Marnick
```
**Bot Response**:  
Displays a list of events Marnick is participating in or has declined.

---

## Command: `/get_activity`
**Description**:  
Retrieve detailed information about a specific activity available at an event, such as special amenities or scheduled programs.

**How to Use**:  
Type `/get_activity` and provide the activity name when prompted.

**Example**:  
```
/get_activity activity_name:Buffet Facts
```
**Bot Response**:  
Displays details about the "Buffet Facts" activity.

---

## Command: `/register_for_event`
**Description**:  
Sign up to participate in an event and provide extra details like the number of people or droids you’ll bring, as well as additional notes.

**How to Use**:  
Type `/register_for_event` and provide the event name and required details.

**Example**:  
```
/register_for_event event_name:Facts Fall 2025 will_attend:Yes person_count:2 droid_count:1 description:Bringing 2 family members and an extra mouse droid.
```
**Bot Response**:  
- If successful: "You have successfully registered for 'Facts Fall 2025'."
- If unsuccessful: "Registration failed. Please check your details and try again."

---

## Command: `/register_for_activity`
**Description**:  
Sign up to participate in a special activity at an event.

**How to Use**:  
Type `/register_for_activity` and provide the activity name.

**Example**:  
```
/register_for_activity activity_name:Dinner
```
**Bot Response**:  
- If successful: "You have successfully registered for the Dinner activity."
- If unsuccessful: "Registration failed. Please check the activity name and try again."

---

## Command: `/update_registration`
**Description**:  
Update your registration details for an event, such as changing the number of droids you'll bring or updating your description.

**How to Use**:  
Type `/update_registration` and provide the event name and updated details.

**Example**:  
```
/update_registration event_name:Facts Fall 2025 droid_count:2 description:Bringing 2 droids and an additional guest.
```
**Bot Response**:  
- If successful: "Your registration for 'Facts Fall 2025' has been updated."
- If unsuccessful: "Update failed. Please check your details and try again."

---

## Command: `/delete_registration`
**Description**:  
Unregister from an event by deleting your registration details.

**How to Use**:  
Type `/delete_registration` and provide the event name.

**Example**:  
```
/delete_registration event_name:Facts Fall 2025
```
**Bot Response**:  
- If successful: "Your registration for 'Facts Fall 2025' has been deleted."
- If unsuccessful: "Deletion failed. Please check the event name and try again."

---

## Notes
- Ensure you are registered (`/register`) before using other commands.
- Provide accurate details when registering or updating your participation.
- Use the `/help` command for additional assistance.

---

# 2. Bot Commands Admin Guide

---

## Table of Contents
1. [Command: `/create_event`](#command-create_event)
2. [Command: `/update_event`](#command-update_event)
3. [Command: `/delete_event`](#command-delete_event)
4. [Command: `/create_activity`](#command-create_activity)
5. [Command: `/update_activity`](#command-update_activity)
6. [Command: `/create_event_channel`](#command-create_event_channel)
7. [Command: `/update_event_channel`](#command-update_event_channel)
8. [Command: `/archive_event_channel`](#command-archive_event_channel)
9. [Command: `/export_event_data`](#command-export_event_data)
10. [Command: `/add_non_discord_user`](#command-add_non_discord_user)
11. [Command: `/update_event_non_discord`](#command-update_event_non_discord)
12. [Command: `/remove_event_non_discord`](#command-remove_event_non_discord)

---

## Command: `/create_event`
**Description**:  
Create a new event with optional details such as the venue, dates, times, and additional amenities.

**How to Use**:  
Type `/create_event` and provide the event name and optional details.

**Example**:  
```
/create_event name:Tech Conference 2025 description:Annual tech conference for innovation photo_url:https://example.com/image.jpg venue:Convention Center street:123 Tech St postal_code:12345 city:Tech City country:Countryland dates:15-05-2025,16-05-2025 open_times:09:00,09:00 close_times:17:00,17:00 arrival_time:08:30 public_access:true power_outlets:true travel_expenses_covered:true free_parking:true lunch_provided:true
```
**Bot Response**:  
- If successful: "Event 'Tech Conference 2025' has been created."
- If unsuccessful: "Event creation failed. Please check your details and try again."

---

## Command: `/update_event`
**Description**:  
Update the details of an existing event, such as description, venue, dates, and additional options.

**How to Use**:  
Type `/update_event` and provide the event name and updated details.

**Example**:  
```
/update_event name:Event X description:Updated description venue:New Venue street:123 St postal_code:12345 city:New City country:Country website:http://facts.com dates:01-01-2025,02-01-2025 open_times:10:00,10:00 close_times:18:00,18:00 arrival_time:09:00
```
**Bot Response**:  
- If successful: "Event 'Event X' has been updated."
- If unsuccessful: "Update failed. Please check your details and try again."

---

## Command: `/delete_event`
**Description**:  
Delete an event by its name.

**How to Use**:  
Type `/delete_event` and provide the event name.

**Example**:  
```
/delete_event name:Facts Fall 2025
```
**Bot Response**:  
- If successful: "Event 'Facts Fall 2025' has been deleted."
- If unsuccessful: "Deletion failed. Please check the event name and try again."

---

## Command: `/create_activity`
**Description**:  
Add a special activity or amenity to an event.

**How to Use**:  
Type `/create_activity` and provide the activity name, event name, and optional details.

**Example**:  
```
/create_activity name:Buffet event_name:Facts Fall 2025 date:01-01-2025 time:19:00 price:35 description:Buffet at Holiday Inn
```
**Bot Response**:  
- If successful: "Activity 'Buffet' has been created for event 'Facts Fall 2025'."
- If unsuccessful: "Activity creation failed. Please check your details and try again."

---

## Command: `/update_activity`
**Description**:  
Update the details of an existing activity for an event.

**How to Use**:  
Type `/update_activity` and provide the activity name, event name, and updated details.

**Example**:  
```
/update_activity activity_name:Buffet event_name:Facts Fall 2025 date:01-01-2025 time:10:00 price:20 description:Bring something
```
**Bot Response**:  
- If successful: "Activity 'Buffet' for event 'Facts Fall 2025' has been updated."
- If unsuccessful: "Update failed. Please check your details and try again."

---

## Command: `/create_event_channel`
**Description**:  
Create a new channel for an event.

**How to Use**:  
Type `/create_event_channel` and provide the event name and cancellation status.

**Example**:  
```
/create_event_channel event_name:Facts Fall 2025 is_cancelled:False
```
**Bot Response**:  
- If successful: "Channel for event 'Facts Fall 2025' has been created."
- If unsuccessful: "Channel creation failed. Please check your details and try again."

---

## Command: `/update_event_channel`
**Description**:  
Update the name or status of an event channel (e.g., whether it’s cancelled).

**How to Use**:  
Type `/update_event_channel` and provide the event name and updated details.

**Example**:  
```
/update_event_channel event_name:Facts Fall 2025 is_cancelled:True
```
**Bot Response**:  
- If successful: "Channel for event 'Facts Fall 2025' has been updated."
- If unsuccessful: "Update failed. Please check your details and try again."

---

## Command: `/archive_event_channel`
**Description**:  
Move an event channel to the archive.

**How to Use**:  
Type `/archive_event_channel` and provide the event name.

**Example**:  
```
/archive_event_channel event_name:Facts Fall 2025
```
**Bot Response**:  
- If successful: "Channel for event 'Facts Fall 2025' has been archived."
- If unsuccessful: "Archiving failed. Please check the event name and try again."

---

## Command: `/export_event_data`
**Description**:  
Export the event data as an Excel file.

**How to Use**:  
Type `/export_event_data` and provide the event name.

**Example**:  
```
/export_event_data event_name:Facts Fall 2025
```
**Bot Response**:  
- If successful: "Data for event 'Facts Fall 2025' has been exported."
- If unsuccessful: "Export failed. Please check the event name and try again."

---

## Command: `/add_non_discord_user`
**Description**:  
Add a new non-Discord user to the database by providing a unique identifier (e.g., email).

**How to Use**:  
Type `/add_non_discord_user` and provide the user's unique identifier and full name.

**Example**:  
```
/add_non_discord_user name:Marnick Michielsen email:marnick.michielsen@proximus.be
```
**Bot Response**:  
- If successful: "User 'Marnick Michielsen' has been added."
- If unsuccessful: "User addition failed. Please check your details and try again."

---

## Command: `/update_event_non_discord`
**Description**:  
Update or add the event participation status for a non-Discord user (confirmed or declined).

**How to Use**:  
Type `/update_event_non_discord` and provide the user's identifier, event name, and status.

**Example**:  
```
/update_event_non_discord identifier:Marnick Michielsen event_name:Facts Fall 2025 status:confirmed
```
**Bot Response**:  
- If successful: "Participation status for 'Marnick Michielsen' in event 'Facts Fall 2025' has been updated."
- If unsuccessful: "Update failed. Please check your details and try again."

---

## Command: `/remove_event_non_discord`
**Description**:  
Remove a non-Discord user’s participation in an event.

**How to Use**:  
Type `/remove_event_non_discord` and provide the user's identifier and event name.

**Example**:  
```
/remove_event_non_discord identifier:Marnick Michielsen event_name:Facts Fall 2025
```
**Bot Response**:  
- If successful: "User 'Marnick Michielsen' has been removed from event 'Facts Fall 2025'."
- If unsuccessful: "Removal failed. Please check your details and try again."

---

## Notes
- Ensure you provide accurate details when creating or updating events and activities.
- Use the `/help` command for additional assistance.

---

## Contributing
If you'd like to contribute to this project, please fork the repository and submit a pull request. For major changes, open an issue first to discuss the proposed changes.

---

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Contact
For questions or support, please contact [Your Name] at [your.email@example.com].

---

Thank you for using the Event Management Bot! 🚀

