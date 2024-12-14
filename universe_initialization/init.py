from pymongo import MongoClient
from tokyog import tokyog

# MongoDB connection
client = MongoClient("mongodb+srv://abdurazzoqov057:yqW7tgxtYjcROPkM@cluster0.ttusl.mongodb.net/?retryWrites=true&w=majority")
db = client.aniverse_db  # Use your database name

# counter = 0

# universes = [
#     "🪸 Ван пис", [200,46,33,63,35,23], # done
#     "🍀 Чёрный клевер", [112,32,26,19,25,10], # done
#     "🗡 Блич", [89,11,15,31,12,20], # done
#     "🍥 Наруто", [133,35,26,28,26,18], # done
#     "🎩 ДжоДжо", [88,21,16,29,13,9], # done 
#     "🐜 Хантер × Хантер", [107,36,27,26,12,6], # done
#     "🥀 Токийский Гуль", [88,30,23,16,11,8], # done
#     "👊 Ванпанчмен", [100,23,26,23,16,12], # done
#     "👺 Истребитель демонов", [90,32,14,23,13,8], # done
#     "🪚 Человек бензопила", [83,27,19,16,11,10], # done
#     "🍎 Повесть о конце света", [91,45,21,8,7,10], # done
#     "⚽️ Синяя тюрьма", [91,26,22,20,13,10], # done
#     "🪄 Магическая битва", [85,19,25,17,13,11], # done
#     "🧤 Моя геройская академия", [114,25,26,27,24,12], # done
#     "🐷 Семь смертных грехов", [153,53,36,26,23,15], # done
#     "⚔️ Берсерк", [95,36,28,13,9,9], # done
#     "🩻 Атака титанов", [133,77,22,14,10,10], # done
#     "📓 Тетрадь смерти", [81,42,12,10,5,12], # done
#     "🧚 Хвост феи", [142,33,43,34,22,10], # done
#     "☀️ Сага о Винланде", [80,35,20,9,7,9], # done
#     "⏱️ Токийские мстители", [90,38,21,12,10,9], # done
#     "🔮 Моб Психо 100", [105,47,26,12,11,9], # done
#     "⚾️ Покемон", [273,89,63,53,35,28], # done
#     "☄️ Драгонболл", [192,65,40,34,34,19], # done
#     "♟ Сололевелинг", [199,68,44,42,27,18], # done
# ]


# for element in universes:
#     counter += 1
#     if counter % 2 == 0:
#         universe_name = universes[counter-2]
#         maximum = universes[counter-1]
#         db.universes.insert_one({
#             "name":universe_name,
#             "maximum":maximum
#         })
    
# print("Success")

for element in tokyog:
    db.bleach_data.insert_one({
        "id": element["id"],
        "name": element["name"],
        "rarity": element["rarity"],
        "attack": element["attack"],
        "health": element["health"],
        "value": element["value"],
        "image_url": element["image_url"]
    })

print("Success")