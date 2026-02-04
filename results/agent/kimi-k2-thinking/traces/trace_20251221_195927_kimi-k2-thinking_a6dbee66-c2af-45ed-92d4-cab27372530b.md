```mermaid
graph TD
node_0[User: 你是一名资深有机合成与波谱解析专家，正在一个虚拟实验室中 分析编号为 a6dbee66-c2af-4...]
node_1[AI: Call Check_Data]
node_0 --> node_1
node_2[Tool: {'result': ['Measure_MW', 'Measure_Formula', 'Get_...]
node_1 --> node_2
node_3[AI: Call Measure_MW, Measure_Formula]
node_2 --> node_3
node_4[Tool: {"result": 222.128965564}]
node_3 --> node_4
node_5[Tool: {"result": "C10H22O3S"}]
node_4 --> node_5
node_6[AI: ]
node_5 --> node_6
```