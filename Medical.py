import os
import json
from py2neo import Graph, Node
from tqdm import tqdm


class MedicalGraph:
    def __init__(self):
        cur_dir = '/'.join(os.path.abspath(__file__).split('/')[:-1])  # 获取当前目录
        self.data_path = os.path.join(cur_dir, 'data/medical(1).json')  # 拼接数据文件路径
        self.g = Graph(
            'neo4j://localhost:7687',  # 数据库的访问方式地址和开放端口
            user="neo4j",  # 数据库user name,如果没有更改过，应该是neo4j
            password="Lin68686688+")  # 数据库密码

    # 读取文件
    def read_nodes(self):
        # 共7类节点
        drugs = []  # 药品
        foods = []  # 食物
        checks = []  # 检查
        departments = []  # 科室
        producers = []  # 药品大类
        diseases = []  # 疾病
        symptoms = []  # 症状
        disease_infos = []  # 疾病信息
        # 构建节点实体关系
        rels_department = []  # 科室一科室关系
        rels_noteat = []  # 疾病一忌吃食物关系
        rels_doeat = []  # 疾病-宜吃食物关系
        rels_recommandeat = []  # 疾病-推荐吃食物关系
        rels_commonddrug = []  # 疾病一通用药品关系
        rels_recommanddrug = []  # 疾病-热门药品关系
        rels_check = []  # 疾病-检查关系
        rels_drug_producer = []  # 厂商-药物关系
        rels_symptom = []  # 疾病症状关系
        rels_acompany = []  # 疾病并发关系
        rels_category = []  # 疾病与科室之间的关系

        count = 0  # 计数器为了后面的判断
        for data in tqdm(open(self.data_path, encoding='utf-8')):  # 打开数据，并返回迭代器遍历每一行json字符串
            disease_dict = {}
            count += 1
            # if count > 300:
            #     break  # 真实应用中不需要编写，但在本实验中我们需要编写以节省运行时间
            data_json = json.loads(data)  # 解析json字符串提取一条疾病信息
            disease = data_json['name']  # 提取疾病名称
            disease_dict['name'] = disease
            diseases.append(disease)  # 添加disease类型节点到列表
            disease_dict['desc'] = ''  # 保存disease类型节点的属性，方便后续存入数据库
            disease_dict['prevent'] = ''
            disease_dict['cause'] = ''
            disease_dict['easy_get'] = ''
            disease_dict['cure_department'] = ''
            disease_dict['cure_way'] = ''
            disease_dict['cure_lasttime'] = ''
            disease_dict['symptom'] = ''
            disease_dict['cured_prob'] = ''

            for name in ['desc', 'prevent', 'cause', 'get_prob', 'easy_get',
                         'cure_way', 'cure_lasttime', 'cured_prob']:  # 遍历简单属性
                if name in data_json:  # 判断简单属性是否存在于疾病信息中
                    disease_dict[name] = data_json[name]  # 若存在就保存

            if 'symptom' in data_json:  # 判断疾病信息中是否有symptom
                symptoms += data_json['symptom']  # 保存symptom节点
                for symptom in data_json['symptom']:
                    rels_symptom.append([disease, symptom])  # 保存'疾病--症状'关系

            if 'acompany' in data_json:  # 判断疾病信息中是否有acompany
                for acompany in data_json['acompany']:  # 遍历并发症列表
                    rels_acompany.append([disease, acompany])  # 保存'疾病--并发症'关系

            if 'cure_department' in data_json:  # 判断疾病信息中是否有cure department
                cure_department = data_json['cure_department']  # 提取治疗科室是一个列表
                if len(cure_department) == 1:  # 科室只有一个
                    rels_category.append([disease, cure_department[0]])  # 添加c疾病-科室'关系
                if len(cure_department) == 2:  # 科室有两个一级科室--二级科室
                    big = cure_department[0]  # 一级科室
                    small = cure_department[1]
                    # 二级科室
                    rels_department.append([small, big])  # 添加"一级科室--二级科室”关系
                    rels_category.append([disease, small])  # 添加“疾病--科室'关系
                disease_dict['cure_department'] = cure_department
                departments += cure_department  # 添加department节点

            if 'common_drug' in data_json:  # 判断疾病信息中是否有common_drug
                common_drug = data_json['common_drug']
                for drug in common_drug:  # 遍历常用药
                    rels_commonddrug.append([disease, drug])  # 添加疾病-常用药关系
                drugs += common_drug  # 添加drug节点

            if 'recommand_drug' in data_json:  # 判断疾病信息中是否有recommand_drug
                recommand_drug = data_json['recommand_drug']
                drugs += recommand_drug  # 添加drug节点
                for drug in recommand_drug:  # 遍历推荐用药
                    rels_recommanddrug.append([disease, drug])  # 添加疾病-热门药品关系

            if 'not_eat' in data_json:  # 判断疾病信息中是否有not_eat
                not_eat = data_json['not_eat']
                for _not in not_eat:  # 遍历忌口食物
                    rels_noteat.append([disease, _not])  # 添加疾病--忌口食物'关系
                foods += not_eat  # 添加food节点

            if 'do_eat' in data_json:
                do_eat = data_json['do_eat']
                for _do in do_eat:
                    rels_doeat.append([disease, _do])  # 添加疾病一宜吃食物关系
                foods += do_eat  # 添加food节点

            if 'check' in data_json:
                check = data_json['check']
                for _check in check:
                    rels_check.append([disease, _check])  # 添加疾病-检查关系
                checks += check  # 添加check节点

            if 'drug_detail' in data_json:
                drug_detail = data_json['drug_detail']
                producer = [i.split('(')[0] for i in drug_detail]  # 提取药品厂家
                # 添加药品-厂家关系
                rels_drug_producer += [[i.split('(')[0], i.split('(')[-1].replace(')', '')]
                                       for i in drug_detail]
                producers += producer  # 添加producer节点
            disease_infos.append(disease_dict)
        return (set(drugs), set(foods), set(checks), set(departments),
                set(producers), set(symptoms), set(
            diseases), disease_infos, rels_check, rels_recommandeat,
                rels_noteat, rels_doeat, rels_department, rels_commonddrug,
                rels_drug_producer, rels_recommanddrug,rels_symptom, rels_acompany, rels_category)

    # 建立节点
    def create_node(self, label, nodes):
        # label：字符串，节点的类型标签
        # nodes：列表，该类别所有节点的name属性值
        for node_name in tqdm(nodes):
            node = Node(label, name=node_name)  # 建立节点对象
            self.g.create(node)  # 节点存入数据库

    # 创建知识图谱中心疾病的节点
    def create_diseases_nodes(self, disease_infos):
        # disease_infos：列表，每个元素是一个疾病字典，包含每个疾病节点的name、desc等属性
        for disease_dict in tqdm(disease_infos):
            node = Node("Disease",
                        name=disease_dict['name'],
                        desc=disease_dict['desc'],
                        prevent=disease_dict['prevent'],
                        cause=disease_dict['cause'],
                        easy_get=disease_dict['easy_get'],
                        cure_lasttime=disease_dict['cure_lasttime'],
                        cure_department=disease_dict['cure_department'],
                        cure_way=disease_dict['cure_way'],
                        cured_prob=disease_dict['cured_prob'])  # 建立节点对象并指定属性值
            self.g.create(node)  # 存储节点到neo4j数据库

    # 创建知识图谱实体节点类型schema
    def create_graphnodes(self):
        # 解析数据并返回结果，结果是一个列表
        data = self.read_nodes()
        self.create_diseases_nodes(data[7])  # disease._infos下标为7
        self.create_node('Drug', data[0])  # Drugs下标为o
        self.create_node('Food', data[1])
        self.create_node('Check', data[2])
        self.create_node('Department', data[3])
        self.create_node('Producer', data[4])
        self.create_node('Symptom', data[5])

    # 创建实体关联边
    def create_relationship(self, start_node, end_node, edges, rel_type, rel_name):
        # 去重处理保证不创建重复的关系
        # start_node：字符串，起始节点的类型标签
        # end_node：字符串，终止节点的类型标签
        # edges：列表，每个元素是一个元组，分别是起始节点name和终止节点name
        # rel_type：字符串 关系类型标签
        # rel_name：字符串 关系的name属性(中文名称)
        set_edges = []
        for edge in tqdm(edges):  # 遍历所有关系边
            set_edges.append('###'.join(edge))  # 将每个关系边起始节点name和终止节点name拼接成字符串
        for edge in tqdm(set(set_edges)):  # 遍历去重后的关系边
            p, q = edge.split('###')  # 分割成起始节点name和终止节点name
            # 创建cypher语句查询起始节点和终止节点并创建关系
            query = "match(p:%s),(q:%s)where p.name='%s'and q.name='%s'create (p)-[rel:%s{name:'%s'}]->(q)" % (
                start_node, end_node, p, q, rel_type, rel_name)
            try:  # 尝试执行语句处理异常
                self.g.run(query)  # 执行语句
            except Exception as e:  # 报错的话打印错误信息
                print(e)

    # 创建实体关系边
    def create_graphrels(self):
        # 解析数据并返回结果，结果是一个列表包含
        # Drugs,Foods,Checks,Departments,
        # Producers,Symptoms,Diseases,disease_infos,
        # rels check,rels_recommandeat,rels_noteat,
        # rels_doeat,rels_department,rels_commonddrug,
        # rels_drug_producer,rels_recommanddrug,rels_symptom,
        # rels_acompany,rels_category
        data = self.read_nodes()
        print(type(data),len(data))
        # 调用create_relationship方法，指定其实节点类型，终止节点类型，该类型所有关系边数据，关系类型，关系name属性
        # rels recommandeat在data中下标为9后续的其他类型关系边以此类推
        self.create_relationship('Disease', 'Food', data[9], 'recommand_eat', '推荐食谱')
        self.create_relationship('Disease', 'Food', data[10], 'no_eat', '忌吃')
        self.create_relationship('Disease', 'Food', data[11], 'do_eat', '宜吃')
        self.create_relationship('Department', 'Department', data[12], 'belongs_to', '属于')
        self.create_relationship('Disease', 'Drug', data[13], 'common_drug', '常用药品')
        self.create_relationship('Producer', 'Drug', data[14], 'drugs_of', '生产药品')
        self.create_relationship('Disease', 'Drug', data[15], 'recommand_drug', '好评药品')
        self.create_relationship('Disease', 'Check', data[8], 'need_check', '诊断检查')
        self.create_relationship('Disease', 'Symptom', data[16], 'has_symptom', '症状')
        self.create_relationship('Disease', 'Disease', data[17], 'acompany_with', '并发症')
        self.create_relationship('Disease', 'Department', data[18], 'belongs_to', '所属科室')


if __name__ == '__main__':
    # 确保 Neo4j 服务正在运行并且连接参数正确
    print("Attempting to connect to Neo4j and build the medical graph...")
    print(f"Data will be loaded from: {MedicalGraph().data_path}")

    # 清空数据库（可选，用于重复测试，请谨慎操作！）
    # choice = input("Do you want to clear the existing Neo4j database? (yes/NO): ")
    # if choice.lower() == 'yes':
    #     print("Clearing database...")
    #     try:
    #         temp_graph = Graph('neo4j://localhost:7687', user="neo4j", password="Lin68686688+")
    #         temp_graph.delete_all()
    #         print("Database cleared.")
    #     except Exception as e:
    #         print(f"Error clearing database: {e}")

    handler = MedicalGraph()
    print("\nStep 1: Creating graph nodes...")
    handler.create_graphnodes()
    print("Node creation process finished.")

    print("\nStep 2: Creating graph relationships...")
    handler.create_graphrels()
    print("Relationship creation process finished.")

    print("\nMedical graph construction complete.")
    print("You can now query the graph in Neo4j Browser (http://localhost:7474).")
    print("Example query: MATCH (d:Disease {name: '感冒'})-[r]->(n) RETURN d, r, n")
