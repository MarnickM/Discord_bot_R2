from pymongo import MongoClient
import os
from dotenv import load_dotenv
import pandas as pd

# Load environment variables from .env file (optional)
load_dotenv()

# Replace this with your MongoDB connection string
MONGO_URI = os.getenv("mongoDB_url")
# Base directory path for the images folder
images_dir = os.path.join(os.path.dirname(__file__), '../images')

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client['R2Builders']
droids_collection = db['Droids']
non_discord_users = db['Non-discord-users']

droids_data = [
    {"name": "R2-D2", "image_path": os.path.join(images_dir, "r2d2.png")},
    {"name": "C-3PO", "image_path": os.path.join(images_dir, "c3po.png")},
    {"name": "BB-8", "image_path": os.path.join(images_dir, "bb8.png")},
    {"name": "K-2SO", "image_path": os.path.join(images_dir, "k2so.png")},
    {"name": "IG-88", "image_path": os.path.join(images_dir, "ig88.png")},
    {"name": "L3-37", "image_path": os.path.join(images_dir, "l337.png")},
    {"name": "D-O", "image_path": os.path.join(images_dir, "do.png")},
    {"name": "Chopper", "image_path": os.path.join(images_dir, "chopper.png")},
    {"name": "R5-D4", "image_path": os.path.join(images_dir, "r5d4.png")},
    {"name": "HK-47", "image_path": os.path.join(images_dir, "hk47.png")},
    {"name": "Mouse Droid", "image_path": os.path.join(images_dir, "mousedroid.png")},
    {"name": "2-1B", "image_path": os.path.join(images_dir, "21b.png")},
    {"name": "T3-M4", "image_path": os.path.join(images_dir, "t3m4.png")},
    {"name": "EV-9D9", "image_path": os.path.join(images_dir, "ev9d9.png")},
    {"name": "FX-7", "image_path": os.path.join(images_dir, "fx7.png")},
    {"name": "4-LOM", "image_path": os.path.join(images_dir, "4lom.png")},
    {"name": "RA-7", "image_path": os.path.join(images_dir, "ra7.png")},
    {"name": "MSE-6", "image_path": os.path.join(images_dir, "mse6.png")},
    {"name": "CZ-3", "image_path": os.path.join(images_dir, "cz3.png")},
    {"name": "R3-S6", "image_path": os.path.join(images_dir, "r3s6.png")},
    {"name": "R4-P17", "image_path": os.path.join(images_dir, "r4p17.png")},
    {"name": "Q9-0", "image_path": os.path.join(images_dir, "q90.png")},
    {"name": "AP-5", "image_path": os.path.join(images_dir, "ap5.png")},
    {"name": "C1-10P", "image_path": os.path.join(images_dir, "c110p.png")},
    {"name": "BT-1", "image_path": os.path.join(images_dir, "bt1.png")},
    {"name": "0-0-0", "image_path": os.path.join(images_dir, "000.png")},
    {"name": "Gonk Droid", "image_path": os.path.join(images_dir, "gonkdroid.png")},
    {"name": "R1-G4", "image_path": os.path.join(images_dir, "r1g4.png")},
    {"name": "R7-A7", "image_path": os.path.join(images_dir, "r7a7.png")},
    {"name": "R8-B7", "image_path": os.path.join(images_dir, "r8b7.png")},
    {"name": "R6-D8", "image_path": os.path.join(images_dir, "r6d8.png")},
    {"name": "R9-D9", "image_path": os.path.join(images_dir, "r9d9.png")},
    {"name": "R4-M9", "image_path": os.path.join(images_dir, "r4m9.png")},
    {"name": "ME-8D9", "image_path": os.path.join(images_dir, "me8d9.png")},
    {"name": "BD-1", "image_path": os.path.join(images_dir, "bd1.png")},
    {"name": "U-3PO", "image_path": os.path.join(images_dir, "u3po.png")},
    {"name": "GA-97", "image_path": os.path.join(images_dir, "ga97.png")},
    {"name": "BB-9E", "image_path": os.path.join(images_dir, "bb9e.png")},
    {"name": "T0-B1", "image_path": os.path.join(images_dir, "t0b1.png")},
    {"name": "WAC-47", "image_path": os.path.join(images_dir, "wac47.png")},
    {"name": "OOM-9", "image_path": os.path.join(images_dir, "oom9.png")},
    {"name": "DUM-Series Pit Droid", "image_path": os.path.join(images_dir, "dumpsdroid.png")},
    {"name": "EV-A4-D", "image_path": os.path.join(images_dir, "eva4d.png")},
    {"name": "IG-11", "image_path": os.path.join(images_dir, "ig11.png")},
    {"name": "4D-M1N", "image_path": os.path.join(images_dir, "4dm1n.png")},
    {"name": "K-3PO", "image_path": os.path.join(images_dir, "k3po.png")},
    {"name": "R2-KT", "image_path": os.path.join(images_dir, "r2kt.png")},
    {"name": "2-1A", "image_path": os.path.join(images_dir, "21a.png")},
    {"name": "5YQ", "image_path": os.path.join(images_dir, "5yq.png")},
    {"name": "R0-GR", "image_path": os.path.join(images_dir, "r0gr.png")},
    {"name": "IT-O Interrogator", "image_path": os.path.join(images_dir, "ito.png")},
    {"name": "SCORPIO", "image_path": os.path.join(images_dir, "scorpio.png")},
    {"name": "EV-3D", "image_path": os.path.join(images_dir, "ev3d.png")},
    {"name": "B1-Series Battle Droid", "image_path": os.path.join(images_dir, "b1droid.png")},
    {"name": "R5-X2", "image_path": os.path.join(images_dir, "r5x2.png")},
    {"name": "Q5-9", "image_path": os.path.join(images_dir, "q59.png")},
    {"name": "CB-23", "image_path": os.path.join(images_dir, "cb23.png")},
    {"name": "Viper Probe Droid", "image_path": os.path.join(images_dir, "viperprobedroid.png")},
    {"name": "R3-A3", "image_path": os.path.join(images_dir, "r3a3.png")},
    {"name": "AP-7", "image_path": os.path.join(images_dir, "ap7.png")},
    {"name": "FX-6", "image_path": os.path.join(images_dir, "fx6.png")},
    {"name": "TA-175", "image_path": os.path.join(images_dir, "ta175.png")},
    {"name": "M-TD", "image_path": os.path.join(images_dir, "mtd.png")},
    {"name": "2BB-2", "image_path": os.path.join(images_dir, "2bb2.png")},
    {"name": "R2-M5", "image_path": os.path.join(images_dir, "r2m5.png")},
    {"name": "R2-KT", "image_path": os.path.join(images_dir, "r2kt.png")},
    {"name": "R2-B1", "image_path": os.path.join(images_dir, "r2b1.png")},
    {"name": "C2-B5", "image_path": os.path.join(images_dir, "c2b5.png")},
    {"name": "T7-01", "image_path": os.path.join(images_dir, "t701.png")}
]


# # Insert data into the 'Droids' collection
# try:
#     # Remove existing entries to avoid duplicates
#     droids_collection.delete_many({})
    
#     # Insert droid data
#     result = droids_collection.insert_many(droids_data)
#     print(f"Inserted {len(result.inserted_ids)} droids into the collection.")
# except Exception as e:
#     print(f"An error occurred: {e}")
# finally:
#     client.close()

excel_file_path = r"C:\\Users\\Marni\\Desktop\\Other\\R2_builders_bot\\csv\\Lijsten Facts\\Facts October 2023 -__ 27-06-2023.xlsx"

# Function to import data from Excel
def import_non_discord_users_from_excel(file_path):
    try:
        # Read the Excel file
        data = pd.read_excel(file_path)
        
        # Process each row
        for index, row in data.iterrows():
            # Extract relevant fields, handling NaN and trimming whitespace
            naam = str(row.get("Naam", "")).strip()
            email = str(row.get("Email", "")).strip()
            country = str(row.get("Country", "")).strip()

            # Validate required fields
            if not naam or not country:
                print(f"Row {index} skipped: Missing Naam or Country. Data: {row.to_dict()}")
                continue
            
            # Handle multiple emails (split by semicolon if needed)
            emails = [e.strip() for e in email.split(";") if e.strip()] if email else ["No email provided"]

            # Insert each email as a separate document if necessary
            for email in emails:
                # Check for duplicate based on email
                if email != "No email provided" and non_discord_users.find_one({"email": email}):
                    print(f"Duplicate found, skipped: {email}")
                    continue

                # Prepare the document for MongoDB
                document = {
                    "name": naam,
                    "email": email,
                    "country": country
                }

                # Insert the document into MongoDB
                non_discord_users.insert_one(document)
                print(f"Inserted: {document}")

        print("Import completed successfully.")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

# Run the import function
# import_non_discord_users_from_excel(excel_file_path)


# Data to be inserted
data = [
    {"name": "Michel Michielsen", "country": "BE", "email": "/"},
    {"name": "Richie Gilbert", "country": "NL", "email": "richie.gilbert@gmail.com"},
    {"name": "Chris Grootjans & Lennert", "country": "BE", "email": "/"},
    {"name": "Chris Williams", "country": "UK", "email": "chris_tcat@hotmail.com"},
    {"name": "Giles Redpath Josh & Kim", "country": "UK", "email": "giles.redpath@ntlworld.com"},
    {"name": "Wim Heirman", "country": "BE", "email": "wim.heirman@telenet.be"},
    {"name": "Jacoba en David", "country": "BE", "email": "gipsybel@gmail.com"},
    {"name": "Eelke Abbink", "country": "NL", "email": "j.e.abbink@gmail.com"},
    {"name": "Christian Dupont", "country": "FR", "email": "christiandup@wanadoo.fr"},
    {"name": "Jeroen Stroeve", "country": "NL", "email": "jeroen@stroevesoer.nl"},
    {"name": "Thorsten Hundsdörfer", "country": "DE", "email": "thorsten.hundsdoerfer@hotmail.de"},
    {"name": "Laurent Deneville", "country": "FR", "email": "laurent@r2builders.fr"},
    {"name": "Yorick Amanda", "country": "BE", "email": "yorick.kyndt@outlook.com"},
    {"name": "Ellen De Clercq", "country": "BE", "email": "declercq_ellen@hotmail.com"},
    {"name": "Laurence Bevan", "country": "UK", "email": "tk1933@outlook.com"},
    {"name": "Soma Stahorszki", "country": "DE", "email": "somastahorszki@gmail.com"},
    {"name": "Jean-Michel MARCHON", "country": "FR", "email": "jmarchon@club-internet.fr"},
    {"name": "Joachim Derycke", "country": "FR", "email": "joejo10@hotmail.com"},
    {"name": "Arnd Riedel", "country": "DE", "email": "arnd2d2@gmx.net"},
    {"name": "Marcus Enk", "country": "DE", "email": "marcus.enk@web.de"},
    {"name": "Mickaël RIOU", "country": "FR", "email": "riou.mickael0603@gmail.com;mickael.riou2015@outlook.fr"},
    {"name": "Simon Battell (Anna & Karen)", "country": "UK", "email": "simonbattell@sky.com"},
    {"name": "Emma Tysoe", "country": "UK", "email": "emtysoe@gmail.com"},
    {"name": "Estelle et POIGNANT Frédéric", "country": "FR", "email": "r2d2fredo76@gmail.com"},
    {"name": "Hennequez Frédéric", "country": "FR", "email": "fr2dh76@gmail.com"},
    {"name": "De Timmerman Vincent", "country": "FR", "email": "vincent.detimmerman@gmail.com"},
    {"name": "Oliver Steeples", "country": "UK", "email": "o.steeples@virgin.net"},
    {"name": "Roel Veldhuyzen", "country": "NL", "email": "roel@roelveldhuyzen.nl"},
    {"name": "Tocqueville Laurent", "country": "FR", "email": "ltocqueville@hotmail.com"},
    {"name": "CLAISSE Sylvain", "country": "FR", "email": "docsly@free.fr"},
    {"name": "Krijn Schaap", "country": "NL", "email": "info@r2builders.nl"}
]

# Insert each entry as a new document
# non_discord_users.insert_many(data)

print("Data inserted successfully")



people_with_emails = [
    {"name": "Wim Heirman", "email": "/"},
    {"name": "Simon Battell", "email": "simonbattell@sky.com"},
    {"name": "Anna Battell", "email": "/"},
    {"name": "Karen Wand", "email": "/"},
    {"name": "Roel Veldhuyzen", "email": "roel@roelveldhuyzen.nl"},
    {"name": "Richie Gilbert", "email": "richie.gilbert@gmail.com"},
    {"name": "Oliver Steeples", "email": "o.steeples@virgin.net"},
    {"name": "Jeanette Müller", "email": "themaverick@themaverick.de"},
    {"name": "Chris Grootjans", "email": "chrisgrootjans@gmail.com"},
    {"name": "Joe Joachim", "email": "joejo10@hotmail.com"},
    {"name": "R2d2 Fredo76", "email": "r2d2fredo76@gmail.com"},
    {"name": "Estelle", "email": "/"},
    {"name": "Giles Redpath", "email": "giles.redpath@ntlworld.com"},
    {"name": "Laurent Devendeville", "email": "laurent@r2builders.fr"},
    {"name": "Laurent Tocqueville", "email": "ltocqueville@hotmail.com"},
    {"name": "Ouessan Factory Cyril Lechevallier", "email": "iphouess@gmail.com"},
    {"name": "Ellen De Clercq", "email": "declercq_ellen@hotmail.com"},
    {"name": "Arnd Riedel", "email": "arnd2d2@gmx.net"},
    {"name": "Christian Dupont", "email": "christiandup@wanadoo.fr"},
    {"name": "Marnick Michielsen", "email": "marnick.michielsen@proximus.be"},
    {"name": "Maxou Michielsen", "email": "Maxou.Michielsen@proximus.be"},
    {"name": "Michel Michielsen", "email": "/"},
    {"name": "Mickael RIOU", "email": "riou.mickael0603@gmail.com"},
    {"name": "Christophe ALBRECHT", "email": "/"},
    {"name": "docsly@free.fr", "email": "docsly@free.fr"},
    {"name": "BigMac Jean Michel", "email": "jmarchon@club-internet.fr"},
    {"name": "Jeroen Stroeve", "email": "jeroen@stroevesoer.nl"},
    {"name": "Bisiaux Stephane", "email": "bisiaux.stephane@free.fr"},
    {"name": "Michael Mathieu", "email": "loup-gris@loup-gris.be"},
    {"name": "Nicolas Le Bris", "email": "lebrisnicolas08@gmail.com"},
    {"name": "Michael Suberg", "email": "michael@suberg.info"},
    {"name": "Poté Pamela", "email": "/"},
    {"name": "Krijn Schaap", "email": "krijnschaap@gmail.com"},
    {"name": "Fred Hennequez", "email": "fr2dh76@gmail.com"},
    {"name": "Emma Tysoe", "email": "emtysoe@gmail.com"},
    {"name": "Chris Williams", "email": "chris_tcat@hotmail.com"},
    {"name": "Osborne Chris", "email": "thechrisosborne@blueyonder.co.uk"},
    {"name": "Martine Vandeweyer", "email": "/"},
    {"name": "Björn Giesler", "email": "bjoern@giesler.de"},
    {"name": "Felix Beyer", "email": "felix.beyer@tum.de"},
    {"name": "Andreas Lukas", "email": "lukas-r2d2@web.de"},
    {"name": "Mark Tadgell", "email": "tadge1970@mail.com"},
    {"name": "Yorick & Amanda", "email": "Yorick.kyndt@outlook.com"}
]


# Loop through each entry in combined and insert/update as needed
for user in people_with_emails:
    name = user["name"]
    email = user["email"]
    
    # Check if the user already exists in the collection by name
    existing_user = non_discord_users.find_one({"name": name})
    
    if existing_user:
        # If the email is "/" in the existing document, update it with the new email
        if existing_user["email"] == "/":
            non_discord_users.update_one({"name": name}, {"$set": {"email": email}})
            print(f"Updated {name}'s email.")
        else:
            print(f"{name} already exists with email {existing_user['email']}, not inserting.")
    else:
        # Insert the new user if they don't exist
        non_discord_users.insert_one(user)
        print(f"Inserted {name} with email {email}.")


