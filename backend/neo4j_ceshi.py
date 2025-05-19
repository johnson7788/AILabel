#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date  : 2024/3/24 19:17
# @File  : neo4j_ceshi.py
# @Author: 
# @Desc  : 一些测试代码
import logging
import requests
import json
import re
from langchain.docstore.document import Document
from langchain_community.document_loaders import TextLoader
from neo4j_vector import Neo4jVector, Neo4jConnect ,remove_lucene_chars
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.embeddings import XinferenceEmbeddings

try:
    embeddings_instance = XinferenceEmbeddings(
        server_url="http://192.168.50.189:9997", model_uid="multilingual-e5-large"
    )
except Exception as e:
    print(f"注意：embeddings_instance初始化失败，错误信息：{e}，请确保向量模型已经启动")
    embeddings_instance = None

username = "neo4j"
password = "welcome123"
url = "bolt://192.168.50.209:7687"
database = "neo4j"

llm_list = [
    {
        "name": "chatgpt",
        "url": "http://127.0.0.1:4636/api/message",
        "ping": "http://127.0.0.1:4636/ping",
        "webapi": False,
    },
    {
        "name": "qwen7B",
        "url": "http://192.168.50.189:36001/worker_generate_stream",
        "ping": f"http://192.168.50.189:36001/health/ready",
        "webapi": False,
    },
    {
        "name": "Yi34B",
        "url": "http://127.0.0.1:9892/api/message",
        "ping": "http://127.0.0.1:9892/ping",
        "webapi": False,
    },
    {
        "name": "Qwen72B",
        "url": "http://127.0.0.1:9890/api/message",
        "ping": "http://127.0.0.1:9890/ping",
        "webapi": False,
    },
    {
        "name": "zhipuapi",
        "url": "http://127.0.0.1:9894/api/message",
        "ping": "http://127.0.0.1:9894/ping",
        "webapi": False,
    },
    {
        "name": "baichuan",
        "url": "http://192.168.50.189:9898/api/chat",
        "ping": "http://192.168.50.189:9898/ping",
        "webapi": True,  # 使用网页爬虫做的api
    },
    {
        "name": "doubao",
        "url": "http://192.168.50.189:9893/api/chat",
        "ping": "http://192.168.50.189:9893/ping",
        "webapi": True,  # 使用网页爬虫做的api
    },
    {
        "name": "kimi",
        "url": "http://192.168.50.189:9895/api/chat",
        "ping": "http://192.168.50.189:9895/ping",
        "webapi": True,  # 使用网页爬虫做的api
    },
    {
        "name": "zhipu",
        "url": "http://192.168.50.189:9899/api/chat",
        "ping": "http://192.168.50.189:9899/ping",
        "webapi": True,  # 使用网页爬虫做的api
    },
    {
        "name": "tongyi",
        "url": "http://192.168.50.189:9896/api/chat",
        "ping": "http://192.168.50.189:9896/ping",
        "webapi": True,  # 使用网页爬虫做的api
    },
    {
        "name": "coze",
        "url": "http://192.168.50.189:9897/api/chat",
        "ping": "http://192.168.50.189:9897/ping",
        "webapi": True,  # 使用网页爬虫做的api
    },
]

def create_vector_from_start():
    """
    从头开始创建向量数据库
    Returns:

    """
    loader = TextLoader("perfume_text.txt")
    documents = loader.load()
    text_splitter = CharacterTextSplitter(separator="\n", chunk_size=1000, chunk_overlap=0)
    docs = text_splitter.split_documents(documents)
    # The Neo4jVector Module will connect to Neo4j and create a vector index if needed.
    db = Neo4jVector.from_documents(
        docs, embeddings_instance, url=url, username=username, password=password
    )
    query = "适合约会的香水有哪些？"
    docs_with_score = db.similarity_search_with_score(query, k=2)

    for doc, score in docs_with_score:
        print("-" * 80)
        print("Score: ", score)
        print(doc.page_content)
        print("-" * 80)

def use_exist_vector_from_start(index_name = "vector"):
    """
    使用已存在的向量库索引
    Returns:

    """
    # The Neo4jVector Module will connect to Neo4j and create a vector index if needed.
    db = Neo4jVector.from_existing_index(
        embeddings_instance,
        url=url,
        username=username,
        password=password,
        index_name=index_name,
    )

    query = "适合约会的香水有哪些？"
    docs_with_score = db.similarity_search_with_score(query, k=2)

    for doc, score in docs_with_score:
        print("-" * 80)
        print("Score: ", score)
        print(doc.page_content)
        print("-" * 80)
def insert_data_vector(index_name = "people"):
    """
    只能用于插入数据，插入后使用initialize_vector_index，给数据创建embedding
    感觉这种方法比较灵活
    Returns:
    """
    # The Neo4jVector Module will connect to Neo4j and create a vector index if needed.
    db = Neo4jVector.from_existing_index(
        embeddings_instance,
        url=url,
        username=username,
        password=password,
        index_name=index_name,
    )
    # 插入3条数据, 这3条数据不带向量检索，需要使用initialize_vector_index进行生成向量检索，即使用from_existing_graph 创建向量
    db.query("CREATE (p:Person {name: 'Tomaz', location:'Slovenia', hobby:'Bicycle'})")
    db.query("CREATE (p:Person {name: 'Petter', location:'Beijing', hobby:'Swiming'})")
    db.query("CREATE (p:Person {name: 'Lucy', location:'Syney', hobby:'Running'})")
    #这个add_documents会创建对应的向量检索，很方便,对应的page_content和metadata需要填写才行, 注意metadata中的id和text是必须的
    db.add_documents([Document(page_content="hello Johnson", metadata={"id": "myid","text":"meta text content" ,"name": "Johnson", "location": "New York", "hobby": "Cooking"})])
    db.add_documents([Document(page_content="hello David", metadata={"id": "did","text":"david text content" ,"name": "David", "location": "England", "hobby": "skating"})])
    docs_with_score = db.similarity_search_with_score("johnson")
    print(docs_with_score[0])

def initialize_vector_index(index_name = "people"):
    """
    初始化向量索引
    Returns:
    """
    # 给已有图数据创建embedding, text_node_properties是把哪些维度作为向量检索的原始文本
    existing_graph = Neo4jVector.from_existing_graph(
        embedding=embeddings_instance,
        url=url,
        username=username,
        password=password,
        index_name=index_name,
        node_label="Person",
        text_node_properties=["name", "location"],
        embedding_node_property="embedding",
    )
    result = existing_graph.similarity_search("beijing", k=1)
    print(result[0])

def hybrid_search_neo4j():
    """
    混合搜索，向量索引和关键字索引.使用search_type创建不同的搜索模式
    Returns:
    """
    #自动创建向量检索和keyword的FULLTEXT检索, 如果已经有了向量索引和关键字索引，那么使用from_existing_index方法
    # 创建的embedding索引名称是index,创建的FULLTEXT检索是keyword
    hybrid_db = Neo4jVector.from_documents(
        docs,
        embeddings_instance,
        url=url,
        username=username,
        password=password,
        search_type="hybrid",
    )
    result = hybrid_db.similarity_search("beijing", k=1)
    print(result[0])

def has_existing_index():
    """
    已经有了混合检索，那么开始使用它
    Returns:
    """
    index_name = "vector"  # default index name
    keyword_index_name = "keyword"  # default keyword index name

    hybrid_db = Neo4jVector.from_existing_index(
        embeddings_instance,
        url=url,
        username=username,
        password=password,
        index_name=index_name,
        keyword_index_name=keyword_index_name,
        search_type="hybrid",
    )
    result = hybrid_db.similarity_search("贵族匠心系列", k=1, with_relation=True) # with_relation根据节点的id进行查询相关内容
    print(result[0])

def chatgpt_generate(question, prompt="", usecache=True):
    """
    单个prompt和问题，可以没有prompt
    Args:
        messages ():
        prompt ():
    Returns:
    """
    logging.info(f"开始使用Chatgpt模型生成, 问题是：{question}\n prompt是: {prompt}")
    url = [llm for llm in llm_list if llm["name"] == "chatgpt"][0]["url"]
    # 把前端传过来的messages换成openai的格式
    new_messages = []
    if prompt:
        new_messages.append({"role": "system", "content": prompt})
    new_messages.append({"role": "user", "content": question})
    params = {'message': new_messages, "temperature": 0.5, "usecache": usecache}
    headers = {'content-type': 'application/json'}
    logging.info(f"Chatgpt的请求参数是：{params}")
    r = requests.post(url, headers=headers, data=json.dumps(params), timeout=1200)
    result = r.json()
    return result

class FoodNeo4j(object):
    """
    食品领域的接口和配置
    """
    def __init__(self):
        self.prompt = """你是一个情感分析抽取模型，请根据评论提取其中的情感关系四元组。
13种关系包括包装，便捷程度，场景，服务，价格，口感，味道, 烹饪方法，皮，气味，外形，馅料，质量缺陷，每种的主要包括的维度是
皮包括皮原料,皮厚度,软硬度,弹韧度,清爽度,粗细度,耐烹饪性,皮喜好度等
馅料包括馅配料,馅料量,馅料新鲜度,馅料紧实度,馅料拉丝度,馅料添加剂,馅料安全度,馅料喜好度等
口感包括口感喜好度,口感细节,汁水等
味道包括味道喜好度,味道感受,鲜美度,甜度,咸度,辣度,酸度,味道浓淡,具体味道等
气味包括气味感受,具体气味,气味喜好度等
外形包括个头,饱满度,外观,紧实度,破损度,外形喜好度等
烹饪方法包括烹饪方法词等
质量缺陷包括吃出异物,食品腐坏,有异味,食用后不良反应,日期不新鲜,包装胀气等
便捷程度包括便捷相关词语等
场景包括用餐时间,节假时节,用餐人数,具体情境,健康宣称,用餐搭配,情绪价值等
包装包括包装设计外观,密封性,取用难易度,可持续性,存放难易度,包装托盒,包装质量等
服务包括客服,售后,配送,物流包装等
价格包括价格合理度,比价,价格变动,性价比等
每个四元组应该包括主体（食物名称）、关系(13种的一种,评论最后已经给出),客体（评论中具体描述词语,评论最后已经给出）,主客体情感(积极，消极，
中性，3种的一种）。
答案中至少包含给出的关系和客体，并补全主体和主客体情感，评论是：<{question}>
请按照以下格式提取关系四元组列表,无需多余解释。
(主体,关系,客体,主客体情感)
(主体,关系,客体,主客体情感)
"""
        self.node_mapper = {
            "食品": "Food",
            "口感": "Texture",
            "馅料": "Stuffing",
            "包装": "Package",
            "便捷程度": "Convenience",
            "场景": "Scene",
            "皮": "Skin",
            "味道": "Taste",
            "气味": "Smell",
            "外形": "Appearance",
            "烹饪方法": "Cooking",
            "质量缺陷": "Quality",
            "服务": "Service",
            "价格": "Price",
        }
        self.name2node = {v:k for k,v in self.node_mapper.items()}
        self.node2color = {
            "Food": "#03c4b1",
            "Texture": "#F3DDEB",
            "Stuffing": "#E8ECEC",
            "Package": "#ECE2EB",
            "Convenience": "#FDF4F3",
            "Scene": "#FFEBD8",
            "Skin": "#D9CEDA",
            "Taste": "#84C9EF",
            "Smell": "#F5E7EF",
            "Appearance": "#CBE0F4",
            "Cooking": "#A1A3B4",
            "Quality": "#DBE1F0",
            "Service": "#F6CBC0",
            "Price": "#EDEDEE",
            "Other": "#F5D8C8",
        }
        self.relation_mapper = {
            "情感": "SENTIMENT_IS"
        }
    def sentiment_extract_model(self,content):
        """
        情感抽取模型
        Returns:
        """
        content = content.replace("\n", "。")
        prompt = self.prompt.replace("<{question}>", content)
        result = chatgpt_generate(question=prompt)
        # 解析输出的格式
        predict_result = result["result"]["content"]
        status, data = self.sentiment_format(predict_result, content)
        if not status:
            return False, "抱歉，解析模型预测结果时出现了格式错误，无法处理这条数据", []
        if not data:
            return False, "抱歉，这条数据没有找到任何情感四元组，请检查提供的数据", []
        status, msg = self.insert2neo4j(data)
        if not status:
            return False, "抱歉，插入数据到neo4j时出现了错误，无法处理这条数据", []
        meta = {"data": data, "plot": "neo4j"}
        return True, msg, meta
    def insert2neo4j(self,data):
        """
        只能用于插入数据，插入后使用initialize_vector_index，给数据创建embedding
        感觉这种方法比较灵活
        Returns:
        """
        #创建一个数据操作实例
        db = Neo4jConnect(
            url=url,
            username=username,
            password=password,
        )
        nodes = []
        for idx, one in enumerate(data):
            cql = one["cql"]
            nodes.extend(one["node_names"])
            try:
                db.query(cql)
            except Exception as e:
                logging.error(f"第{idx}条数据插入数据失败，cql是：{cql},错误是,{e}")
        nodes = list(set(nodes))
        for node_name in nodes:
            # 对插入过的数据构建索引和embedding向量, 默认使用name的属性进行向量化,
            index_name = node_name + "_index"
            existing_graph = Neo4jVector.from_existing_graph(
                embedding=embeddings_instance,
                url=url,
                username=username,
                password=password,
                index_name=index_name,
                node_label=node_name,
                text_node_properties=["name"],
                embedding_node_property="embedding",
            )
        msg = [{'subject': one["subject"], "relation": one["relation"], "object": one["object"], "sentiment":one["sentiment"]} for one in data]
        return True, msg
    def sentiment_format(self,result, content):
        """
        对模型的预测结果进行格式化解析
        Args:
            result ():  模型预测结果
            content: 原始文本
        Returns:
            status, data
        """
        data = []
        lines = re.split('[\n、]',result)
        try:
            for idx, line in enumerate(lines):
                line = line.replace("'","").replace('"','')
                line_new = re.sub(r'\(|\)', '', line)
                all_words = re.split('[,，]', line_new)
                if len(all_words) == 4:
                    data.append({
                        "subject": all_words[0].strip(),
                        "relation": all_words[1].strip(),
                        "object": all_words[2].strip(),
                        "sentiment": all_words[3].strip(),
                        "text": content,
                    })
        except Exception as e:
            return False, f"解析模型输出的格式时，出现了错误，是否可能是模型输出问题，{e}"
        # 对data数据生成cql, 名称对应知识图谱中的节点类型
        clean_content = remove_lucene_chars(content)
        """
        MERGE (n1:Food {name: '羊肉饺子'})
        MERGE (n2:Taste {name: '汁水丰富'})
        MERGE (n1)-[r:SENTIMENT_IS {name: '积极'}]->(n2)
        """
        for idx, one in enumerate(data):
            subject = one["subject"]
            subject_id = one["subject"]
            relation = one["relation"]
            object = one["object"]
            obeject_id = one["object"]
            sentiment = one["sentiment"]
            object_node = self.node_mapper.get(relation,"Other")
            if object_node == "Other":
                # 对于不知道的类型，可以把类型加到其它的维度，方便日后处理
                cql = f"""
                MERGE (n1:Food {{name: '{subject}', text:'{clean_content}', id:'{subject_id}'}})
                MERGE (n2:{object_node} {{name: '{object}', type: {relation}, text:'{clean_content}',id:'{obeject_id}' }})
                MERGE (n1)-[r:SENTIMENT_IS {{name: '{sentiment}'}}]->(n2)
                """
            else:
                cql = f"""
                MERGE (n1:Food {{name: '{subject}', text:'{clean_content}', id:'{subject_id}'}})
                MERGE (n2:{object_node} {{name: '{object}', text:'{clean_content}', id:'{obeject_id}' }})
                MERGE (n1)-[r:SENTIMENT_IS {{name: '{sentiment}'}}]->(n2)
                """
            data[idx]["cql"] = cql
            data[idx]["node_names"] = ["Food",object_node] # 节点类型
            data[idx]["nodes"] = [
                {"name": subject, "text": clean_content, "id": subject_id, "color": self.node2color["Food"], "node_type":"食品"},
                {"name": object, "text": clean_content, "id": obeject_id, "color": self.node2color[object_node], "node_type": relation},
            ]
            #  添加关系，source是原节点id
            data[idx]["links"] = {"source": subject_id, "target": obeject_id, "relation": sentiment,"relation_type":"SENTIMENT_IS"}
        return True, data
    def query_by_property(self, property_name,property_value, node_name=None, limit=20, without_embedding=True):
        """
        根据属性的名称和属性值进行查找
        Args:
            property_name (): 例如id或者name
            property_value (): 属性值
            node_name: 节点的名称，None表示不提供
            without_embedding: 不要embedding信息
            limit: 20，限制返回条数, 如果-1表示不限制
        Returns:
        """
        #创建一个数据操作实例
        db = Neo4jConnect(
            url=url,
            username=username,
            password=password,
        )
        if node_name:
            cql = f'''MATCH p=({node_name} {{{property_name}: "{property_value}"}})-[]-()
            WITH p, relationships(p) AS rels
            RETURN p,
            [rel in rels | properties(rel)] AS rel_properties,
            [rel in nodes(p) | labels(rel)] AS node_labels
            '''
        else:
            cql = f'''MATCH p=({{{property_name}: "{property_value}"}})-[]-()
            WITH p, relationships(p) AS rels
            RETURN p,
            [rel in rels | properties(rel)] AS rel_properties,
            [rel in nodes(p) | labels(rel)] AS node_labels
            '''
        if limit != -1:
            cql += f" LIMIT {limit}"
        query_result = db.query(cql)
        # 给每条数据添加nodes和links，方便d3js展示
        data = []
        for idx, row in enumerate(query_result):
            rowp = row["p"]
            subject = rowp[0]
            relation_name = rowp[1]
            object = rowp[2]
            if without_embedding:
                if "embedding" in subject:
                    del subject["embedding"]
                if "embedding" in object:
                    del object["embedding"]
            subject_node_label = row["node_labels"][0][0]
            subject["color"] = self.node2color[subject_node_label]
            object_node_label = row["node_labels"][1][0]
            object["color"] = self.node2color[object_node_label]
            if "type" in subject:
                subject["node_type"] = subject["type"]
            else:
                subject["node_type"] = subject_node_label
            # 如果属性里面已经有type了，那么就用属性里面的，否则用我们预设的type
            if "type" in object:
                object["node_type"] = object["type"]
            else:
                object["node_type"] = object_node_label
            nodes = [subject,object]
            relation_value = row["rel_properties"][0]["name"]
            links = {"source": subject["id"], "target": object["id"], "relation": relation_value, "relation_type":relation_name}
            one = {"nodes":nodes,"links":links}
            data.append(one)
        return data
    def query_by_search(self, content, node_names=["all"], topk=1,search_type="vector"):
        """
        使用混合搜索搜索neo4j
        Args:
            content (): 要搜索的内容
            node_names: 搜索哪些节点 ["all"] 代表默认搜索所有节点
            search_type: hybrid 或者vector
        Returns:
        """
        if "all" in node_names:
            node_names = list(self.node_mapper.keys())
        index_names = []
        for name in node_names:
            en_name = self.node_mapper.get(name)
            if en_name is None:
                return False, f"输入的节点名称: {name}不存在，请检查", []
            index_names.append(en_name+"_index")
        results = []
        for index_name in index_names:
            try:
                hybrid_db = Neo4jVector.from_existing_index(
                    embeddings_instance,
                    url=url,
                    username=username,
                    password=password,
                    index_name=index_name,
                    search_type=search_type,
                )
            except Exception as e:
                logging.error(f"索引: {index_name} 搜索失败，请检查该索引是否存在")
                continue
            docs_with_score = hybrid_db.similarity_search_with_score(content, k=topk)
            for idx, one in enumerate(docs_with_score):
                one = list(one)
                one.append(index_name)
                results.append(one)
        #排序results, 获取topk，按分数最大的
        results.sort(key=lambda x: x[1], reverse=True)
        topk_results = results[:topk]
        data = []
        for one in topk_results:
            index_name = one[-1]
            node_name = index_name.replace("_index", "")
            metadata = one[0].metadata
            # 获取第1个meta信息
            meta_key = list(metadata.keys())[0]
            query_data = self.query_by_property(property_name=meta_key,property_value=metadata[meta_key],node_name=node_name,limit=1)
            data.append(query_data[0])
        if not data:
            return False, "未找到相关数据", []
        # 返回的msg很重要，LLM会根据msg再次进行summary作为最终结果
        msg = "知识图谱返回的查询结果:\n"
        for one in data:
            nodes = one["nodes"]
            for node in nodes:
                node_type = node["node_type"]
                node_label = self.name2node[node_type]
                msg += f"节点名称是：{node['name']}，节点类型是: {node_label}。"
        meta = {"data": data, "plot": "neo4j"}
        return True, msg, meta
    def count_kg_scope(self):
        # 统计知识图谱的规模
        db = Neo4jConnect(
            url=url,
            username=username,
            password=password,
        )
        data = {}
        msg = "知识图谱的规模统计如下：\n"
        for name, label in self.node_mapper.items():
            cql = "MATCH (n:%s) RETURN count(n)"% label
            result = db.query(cql)
            number = list(result[0].values())[0]
            data[name] = number
            msg += f"节点类型是：{name}，节点数量是：{number}。\n"
        for name, label in self.relation_mapper.items():
            cql = "MATCH ()-[r:%s]->() RETURN count(r)"% label
            result = db.query(cql)
            number = list(result[0].values())[0]
            data[name] = number
            msg += f"关系类型是：{name}，关系数量是：{number}。\n"
        info = {"title": "知识图谱的规模统计", "type": "Bar"} # 一些绘图相关的配置信息
        meta = {"data": data, "plot": "echarts", "info": info}
        return True, msg, meta

if __name__ == '__main__':
    # create_vector_from_start()
    # use_exist_vector_from_start()
    # insert_data_vector()
    # initialize_vector_index()
    # hybrid_search_neo4j()
    # has_existing_index()
    food_instance = FoodNeo4j()
    # food_instance.sentiment_extract_model(content="徐州的朋友投喂了她们那里一家看上去口碑不错的羊肉包子店出的牛羊肉馅，我一下子想起来是好久没吃过羊肉馅饺子了，以前旧房子那边有个东北餐馆做得还不错，搬家以后好像就没吃过了。新鲜包的羊肉饺子果然味道不错，馅里汁水丰富，我平时不是很爱吃饺子的也吃了15个。要是手擀皮应该更好点，因为买的皮子多少有点薄了，又包得大，很小心了还是煮破了几个。那点评上说这家店的羊肉包子他一口气吃了6个，我觉得这味道做成包子，我恐怕也能行。剩下的肉馅我想做包子，做馅饼，但我还有好多对联要写。")
    # food_instance.sentiment_extract_model(content="东北日记：稳稳地很幸福昨天我们充当女德华带了一个特别乖和一个特别淘气的小孩都超级可爱晚上唱首歌家里给了六百我和我妹妹分家里打牌冲动发钱人在家中坐钱从天上来我舅还是一如既往的不着调我小时候他二十岁就欺负我现在我二十岁他四十岁还拿着烟花吓我欺负我昨天晚上特别饿我弟给我和萌萌炒米饭香晕结果打牌那屋也饿了晚上十一点我们家硬是吃了第四顿饭最后一张照片是我姥姥做的豆浆巨巨巨浓郁现在还在做豆腐等着投喂有一天晚上就结婚问题大胆输出我的观点我姥爷我妈我大舅支持我我小姥不支持但是没关系被反驳回去了自己烟花玩完了只能蹭蹭别人家的东北大炕睡的太舒服了每天腰都暖的.")
    # food_instance.query_by_property(property_name="id",property_value="羊肉饺子")
    # food_instance.query_by_search(content="找出羊肉饺子相关的内容",topk=2)
    food_instance.count_kg_scope()