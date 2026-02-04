```mermaid
graph TD
node_0[User: 你是一名资深有机合成与波谱解析专家，正在一个虚拟实验室中 分析编号为 cd5fbbde-c8aa-4636-bc2f-631c05f48e46 的未知有机小分子...]
node_1[AI: Call Check_Data, Measure_Formula, Measure_MW]
node_0 --> node_1
node_2[Tool: Check_Data (success): {'result': ('Measure_MW', 'Measure_Formula', 'Get_1H_NMR', 'Get_13C_NMR', 'Get_H...]
node_1 --> node_2
node_3[Tool: Measure_Formula (success): {'result': 'C14H12O2'}]
node_2 --> node_3
node_4[Tool: Measure_MW (success): {'result': 212.083729624}]
node_3 --> node_4
node_5[AI: Call Get_1H_NMR, Get_13C_NMR]
node_4 --> node_5
node_6[Tool: Get_1H_NMR (success): {'result': 'δ 8.10 (d, J = 8.4 Hz, 2H), 7.65 (d, J = 8.4 Hz, 2H), 7.63 (d, J = 6...]
node_5 --> node_6
node_7[Tool: Get_13C_NMR (success): {'result': 'δ 167.0, 145.6, 140.0, 130.1, 128.9, 128.8, 128.1, 127.3, 127.0, 52....]
node_6 --> node_7
node_8[AI: {'type': 'text', 'text': '根据现有谱学数据，对样品 cd5fbbde-c8aa-4636-bc2f-631c05f48e46 的结构解...]
node_7 --> node_8
```