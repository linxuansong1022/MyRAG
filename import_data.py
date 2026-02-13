#!/usr/bin/env python3
"""
直接导入数据到 Neo4j
"""
import csv
from neo4j import GraphDatabase

# Neo4j 连接配置
URI = "bolt://localhost:7687"
USER = "neo4j"
PASSWORD = "12345678"

def import_data():
    driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))
    
    with driver.session() as session:
        # 创建约束
        print("创建约束...")
        session.run("CREATE CONSTRAINT recipe_id_unique IF NOT EXISTS FOR (r:Recipe) REQUIRE r.nodeId IS UNIQUE")
        session.run("CREATE CONSTRAINT ingredient_id_unique IF NOT EXISTS FOR (i:Ingredient) REQUIRE i.nodeId IS UNIQUE")
        session.run("CREATE CONSTRAINT cookingstep_id_unique IF NOT EXISTS FOR (s:CookingStep) REQUIRE s.nodeId IS UNIQUE")
        
        # 导入节点
        print("导入节点...")
        with open('/Users/songlinxuan/Desktop/my-graph-rag/data/cypher/nodes.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            recipes = []
            ingredients = []
            steps = []
            
            for row in reader:
                if row['nodeId'] < '200000000':
                    continue
                    
                if row['labels'] == 'Recipe':
                    recipes.append({
                        'nodeId': row['nodeId'],
                        'name': row['name'],
                        'description': row.get('description', ''),
                        'difficulty': float(row['difficulty']) if row.get('difficulty') else None,
                        'category': row.get('category', ''),
                        'cuisineType': row.get('cuisineType', '')
                    })
                elif row['labels'] == 'Ingredient':
                    ingredients.append({
                        'nodeId': row['nodeId'],
                        'name': row['name'],
                        'category': row.get('category', ''),
                        'amount': row.get('amount', ''),
                        'unit': row.get('unit', '')
                    })
                elif row['labels'] == 'CookingStep':
                    steps.append({
                        'nodeId': row['nodeId'],
                        'name': row['name'],
                        'description': row.get('description', ''),
                        'stepNumber': float(row['stepNumber']) if row.get('stepNumber') else None,
                        'methods': row.get('methods', ''),
                        'tools': row.get('tools', '')
                    })
            
            print(f"准备导入 {len(recipes)} 个菜谱, {len(ingredients)} 个食材, {len(steps)} 个步骤")
            
            # 批量创建节点
            if recipes:
                session.run("""
                    UNWIND $recipes AS recipe
                    MERGE (r:Recipe {nodeId: recipe.nodeId})
                    SET r.name = recipe.name,
                        r.description = recipe.description,
                        r.difficulty = recipe.difficulty,
                        r.category = recipe.category,
                        r.cuisineType = recipe.cuisineType
                """, recipes=recipes)
                print(f"✓ 导入了 {len(recipes)} 个菜谱")
            
            if ingredients:
                session.run("""
                    UNWIND $ingredients AS ing
                    MERGE (i:Ingredient {nodeId: ing.nodeId})
                    SET i.name = ing.name,
                        i.category = ing.category,
                        i.amount = ing.amount,
                        i.unit = ing.unit
                """, ingredients=ingredients)
                print(f"✓ 导入了 {len(ingredients)} 个食材")
            
            if steps:
                session.run("""
                    UNWIND $steps AS step
                    MERGE (s:CookingStep {nodeId: step.nodeId})
                    SET s.name = step.name,
                        s.description = step.description,
                        s.stepNumber = step.stepNumber,
                        s.methods = step.methods,
                        s.tools = step.tools
                """, steps=steps)
                print(f"✓ 导入了 {len(steps)} 个烹饪步骤")
        
        # 导入关系
        print("导入关系...")
        with open('/Users/songlinxuan/Desktop/my-graph-rag/data/cypher/relationships.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            requires_rels = []
            contains_rels = []
            
            for row in reader:
                if row['relationshipType'] == '801000001':  # REQUIRES
                    requires_rels.append({
                        'startId': row['startNodeId'],
                        'endId': row['endNodeId'],
                        'amount': row.get('amount', ''),
                        'unit': row.get('unit', '')
                    })
                elif row['relationshipType'] == '801000003':  # CONTAINS_STEP
                    contains_rels.append({
                        'startId': row['startNodeId'],
                        'endId': row['endNodeId'],
                        'stepOrder': float(row['step_order']) if row.get('step_order') else None
                    })
            
            print(f"准备创建 {len(requires_rels)} 个REQUIRES关系, {len(contains_rels)} 个CONTAINS_STEP关系")
            
            # 批量创建关系
            if requires_rels:
                session.run("""
                    UNWIND $rels AS rel
                    MATCH (r:Recipe {nodeId: rel.startId})
                    MATCH (i:Ingredient {nodeId: rel.endId})
                    MERGE (r)-[req:REQUIRES]->(i)
                    SET req.amount = rel.amount,
                        req.unit = rel.unit
                """, rels=requires_rels)
                print(f"✓ 创建了 {len(requires_rels)} 个REQUIRES关系")
            
            if contains_rels:
                session.run("""
                    UNWIND $rels AS rel
                    MATCH (r:Recipe {nodeId: rel.startId})
                    MATCH (s:CookingStep {nodeId: rel.endId})
                    MERGE (r)-[c:CONTAINS_STEP]->(s)
                    SET c.stepOrder = rel.stepOrder
                """, rels=contains_rels)
                print(f"✓ 创建了 {len(contains_rels)} 个CONTAINS_STEP关系")
        
        # 显示统计
        print("\n数据导入完成！统计信息：")
        result = session.run("""
            MATCH (n)
            RETURN labels(n)[0] as NodeType, count(n) as Count
            ORDER BY Count DESC
        """)
        for record in result:
            print(f"  {record['NodeType']}: {record['Count']}")
    
    driver.close()

if __name__ == "__main__":
    import_data()
