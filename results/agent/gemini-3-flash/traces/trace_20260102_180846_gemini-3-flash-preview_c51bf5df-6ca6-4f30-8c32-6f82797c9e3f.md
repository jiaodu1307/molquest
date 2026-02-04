```mermaid
graph TD
node_0[User: 你是一名资深有机合成与波谱解析专家，正在一个虚拟实验室中 分析编号为 c51bf5df-6ca6-4f30-8c32-6f82797c9e3f 的未知有机小分子...]
node_1[AI: Call Measure_MW, Measure_Formula, Calculate_DBE, Check_Data]
node_0 --> node_1
node_2[Tool: Measure_MW (success): {'result': 582.210980936}]
node_1 --> node_2
node_3[Tool: Measure_Formula (success): {'result': 'C32H38O6S2'}]
node_2 --> node_3
node_4[Tool: Calculate_DBE (success): {'result': 14.0}]
node_3 --> node_4
node_5[Tool: Check_Data (success): {'result': ('Measure_MW', 'Measure_Formula', 'Get_1H_NMR', 'Get_13C_NMR', 'Get_H...]
node_4 --> node_5
node_6[AI: Call Get_1H_NMR, Get_13C_NMR]
node_5 --> node_6
node_7[Tool: Get_1H_NMR (success): {'result': '1H NMR (300 MHz, CDCl3): δ 7.40 – 7.27 (m, 8H), 7.26 – 7.15 (m, 6H),...]
node_6 --> node_7
node_8[Tool: Get_13C_NMR (success): {'result': '13C NMR (75 MHz, CDCl3): δ 157.62, 147.79, 139.79, 138.83, 136.05, 1...]
node_7 --> node_8
node_9[AI: Call Get_IR]
node_8 --> node_9
node_10[Tool: Get_IR (error): {'error': 'Sample c51bf5df-6ca6-4f30-8c32-6f82797c9e3f has no 'ir' data.'}]
node_9 --> node_10
node_11[AI: Call Get_HRMS]
node_10 --> node_11
node_12[Tool: Get_HRMS (success): {'result': 'HRMS (ESI+): m/z calc’d for C32H38O6S2Na (M+Na)+: 605.2002, found: 6...]
node_11 --> node_12
node_13[AI: Call Get_Melting_Point]
node_12 --> node_13
node_14[Tool: Get_Melting_Point (success): {'result': '150.5 – 152.7 °C.'}]
node_13 --> node_14
node_15[AI: {'type': 'text', 'text': '自然语言分析：\n该化合物的分子式为 $C_{32}H_{38}O_{6}S_{2}$，不饱和度为 14。H...]
node_14 --> node_15
node_16[AI: {'type': 'text', 'text': '该化合物的分子式为 $C_{32}H_{38}O_{6}S_{2}$，不饱和度为 14。HRMS (m/z ...]
node_15 --> node_16
```