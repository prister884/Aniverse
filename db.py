from pymongo import MongoClient

client = MongoClient("mongodb+srv://abdurazzoqov057:yqW7tgxtYjcROPkM@cluster0.ttusl.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client.aniverse_db  # Use your database name