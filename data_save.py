import pymongo


def save_prepared_data(data_dict):
    for collection_name, data in data_dict.items():
        save_to_mongodb(data, collection_name)

def save_to_mongodb(data, collection_name):
    # Connect to MongoDB
    client = pymongo.MongoClient('mongodb://localhost:27017/')
    db = client['summative']
    try:
        records = data.to_dict('records')
        collection.insert_many(records)
        print(f"Data saved to {collection_name} in MongoDB.")
    except Exception as e:
        print(f"Error saving data to MongoDB: {str(e)}")