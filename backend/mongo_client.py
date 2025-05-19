import pymongo
from bson.objectid import ObjectId

class MongoDBManager(object):
    def __init__(self, host="192.168.50.189", port=27017):
        self.client = pymongo.MongoClient(host, port)

    def create_collection(self, database, collection_name):
        """手动创建方法，一般不需要手动创建，会在使用过程中自动创建的"""
        db = self.client[database]
        collection_list = db.list_collection_names()
        if collection_name in collection_list:
            print(f"集合 {collection_name} 已存在.")
        else:
            db.create_collection(collection_name)
            print(f"集合 {collection_name} 创建成功.")
    def _get_collection(self, database, collection):
        # 获取使用的collection实例
        db = self.client[database]
        return db[collection]

    def insert_data(self, data=[], database='chat', collection='label', clean_before_insert=False, only_clean=False):
        """插入数据"""
        assert isinstance(data, list), "data必须是列表类型"
        mycol = self._get_collection(database, collection)
        if clean_before_insert or only_clean:
            mycol.delete_many({})
            print(f"事先清除已有数据成功: 清除的collection是: {database}中的{collection}")
        if not only_clean:
            x = mycol.insert_many(data)
            print(f"插入成功，插入的id是{x}")

    def read_data(self, database='chat', collection='label', number=-1):
        """获取所有数据"""
        mycol = self._get_collection(database, collection)
        if number == -1:
            data = [x for x in mycol.find()]
            print(f"从mongo数据库{collection}中共搜索到所有数据{len(data)}条")
        else:
            # 获取最后number条数据
            data = [x for x in mycol.find().sort("_id", -1).limit(number)]
            print(f"从mongo数据库{collection}中获取了{len(data)}条数据")
        return data

    def read_data_count(self, database='chat', collection='label'):
        """获取数据总数"""
        mycol = self._get_collection(database, collection)
        count = mycol.count_documents({})
        print(f"mongo数据库{collection}中共有数据{count}条")
        return count
    def find_data(self, query, database='chat', collection='label',number=-1):
        """查询数据"""
        if "_id" in query:
            query["_id"] = ObjectId(query["_id"])
        mycol = self._get_collection(database, collection)
        if number == -1:
            data = [x for x in mycol.find(query)]
            print(f"从mongo数据库{collection}中共搜索到所有数据{len(data)}条")
        else:
            data = [x for x in mycol.find(query).limit(number)]
            print(f"从mongo数据库{collection}中获取了{len(data)}条数据")
        return data

    def delete_one_data(self, query, database='chat', collection='label'):
        """删除一条数据"""
        if "_id" in query:
            query["_id"] = ObjectId(query["_id"])
        mycol = self._get_collection(database, collection)
        result = mycol.delete_one(query)
        if result.deleted_count != 0:
            msg = f"已从mongo数据库{collection}中删除{result.deleted_count}数据。"
            print(msg)
            return True, msg
        else:
            return False, "未找到匹配的数据，所以无法删除任何数据"

    def update_one_data(self, query, new_values, database='chat', collection='label'):
        """更新一条数据
        myquery = { "address": "Valley 345" }
        newvalues = { "$set": { "address": "Canyon 123" } }
        """
        if "_id" in query and isinstance(query["_id"], str):
            query["_id"] = ObjectId(query["_id"])
        mycol = self._get_collection(database, collection)
        # new_values 是一个字典，形如 {"$set": {"key": "new_value"}}，将用于更新数据库里的数据
        result = mycol.update_one(query, new_values)
        if result.modified_count != 0:
            msg = f"已在mongo数据库{collection}中更新了 {result.modified_count} 条数据。"
            print(msg)
            return True, msg
        else:
            return False, "未找到匹配的数据，所以更新任何数据"