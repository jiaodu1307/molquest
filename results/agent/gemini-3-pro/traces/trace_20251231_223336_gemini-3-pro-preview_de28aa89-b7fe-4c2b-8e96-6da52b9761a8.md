```mermaid
graph TD
node_0[User: 你是一名资深有机合成与波谱解析专家，正在一个虚拟实验室中 分析编号为 de28aa89-b7fe-4c2b-8e96-6da52b9761a8 的未知有机小分子...]
node_1[AI: Call Measure_Formula, Measure_MW, Check_Data]
node_0 --> node_1
node_2[Tool: Measure_Formula (success): {'result': 'C21H17FO2'}]
node_1 --> node_2
node_3[Tool: Measure_MW (success): {'result': 320.121258004}]
node_2 --> node_3
node_4[Tool: Check_Data (success): {'result': ('Measure_MW', 'Measure_Formula', 'Get_1H_NMR', 'Get_13C_NMR', 'Get_I...]
node_3 --> node_4
node_5[AI: Call Get_1H_NMR, Get_13C_NMR, Get_IR]
node_4 --> node_5
node_6[Tool: Get_1H_NMR (success): {'result': '1H NMR (300 MHz, CDCl3) δ 2.40 (br s, 6H), 7.15-7.34 (m, 10H). Carbo...]
node_5 --> node_6
node_7[Tool: Get_13C_NMR (success): {'result': '13C NMR (75 MHz, CDCl3, C-F coupling constants assigned where possib...]
node_6 --> node_7
node_8[Tool: Get_IR (success): {'result': 'FT-IR (neat, cm-1) υ 1701, 1469, 1287.'}]
node_7 --> node_8
node_9[AI: Call Get_Melting_Point, Get_MS]
node_8 --> node_9
node_10[Tool: Get_Melting_Point (error): {'error': 'Sample de28aa89-b7fe-4c2b-8e96-6da52b9761a8 has no 'melting_point' da...]
node_9 --> node_10
node_11[Tool: Get_MS (error): {'error': 'Sample de28aa89-b7fe-4c2b-8e96-6da52b9761a8 has no 'ms' data.'}]
node_10 --> node_11
node_12[AI: {'type': 'text', 'text': '基于现有谱学数据，对样品 de28aa89-b7fe-4c2b-8e96-6da52b9761a8 的结构解...]
node_11 --> node_12
```