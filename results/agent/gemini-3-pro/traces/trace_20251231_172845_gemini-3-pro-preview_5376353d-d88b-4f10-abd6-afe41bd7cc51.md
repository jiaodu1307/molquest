```mermaid
graph TD
node_0[User: 你是一名资深有机合成与波谱解析专家，正在一个虚拟实验室中 分析编号为 5376353d-d88b-4f10-abd6-afe41bd7cc51 的未知有机小分子...]
node_1[AI: Call Measure_Formula, Measure_MW, Check_Data]
node_0 --> node_1
node_2[Tool: Measure_Formula (success): {'result': 'C12H9NO2'}]
node_1 --> node_2
node_3[Tool: Measure_MW (success): {'result': 199.063328528}]
node_2 --> node_3
node_4[Tool: Check_Data (success): {'result': ('Measure_MW', 'Measure_Formula', 'Get_1H_NMR', 'Get_13C_NMR', 'Get_H...]
node_3 --> node_4
node_5[AI: Call Get_1H_NMR, Get_13C_NMR]
node_4 --> node_5
node_6[Tool: Get_1H_NMR (success): {'result': 'δ 8.30 (d, J = 8.8 Hz, 2H), 7.74 (d, J = 8.8 Hz, 2H), 7.63 (d, J = 6...]
node_5 --> node_6
node_7[Tool: Get_13C_NMR (success): {'result': 'δ 147.6, 147.1, 138.7, 129.1, 128.9, 127.8, 127.4, 124.1'}]
node_6 --> node_7
node_8[AI: Call Calculate_DBE, Get_IR]
node_7 --> node_8
node_9[Tool: Calculate_DBE (success): {'result': 9.0}]
node_8 --> node_9
node_10[Tool: Get_IR (error): {'error': 'Sample 5376353d-d88b-4f10-abd6-afe41bd7cc51 has no 'ir' data.'}]
node_9 --> node_10
node_11[AI: {'type': 'text', 'text': '通过对现有数据的分析，我已锁定该样品的分子结构。\n\n### 1. 基础数据分析\n* **分子式**: ...]
node_10 --> node_11
```