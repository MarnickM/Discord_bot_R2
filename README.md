# Astromech Bot

# Bot Commands User Guide

This repository contains a bot designed to help users manage event registrations, activities, and participation details. Below is a comprehensive guide to all the available commands and how to use them.

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
