```mermaid
graph TD
node_0[User: 你是一名资深有机合成与波谱解析专家，正在一个虚拟实验室中 分析编号为 971ed2d0-d638-4d90-b4ad-f71ac4cd247d 的未知有机小分子...]
node_1[AI: Call Measure_Formula, Measure_MW, Check_Data]
node_0 --> node_1
node_2[Tool: Measure_Formula (success): {'result': 'C20H26O6S2'}]
node_1 --> node_2
node_3[Tool: Measure_MW (success): {'result': 426.11708055199995}]
node_2 --> node_3
node_4[Tool: Check_Data (success): {'result': ('Measure_MW', 'Measure_Formula', 'Get_1H_NMR', 'Get_13C_NMR', 'Get_H...]
node_3 --> node_4
node_5[AI: Call Get_1H_NMR, Get_13C_NMR]
node_4 --> node_5
node_6[Tool: Get_1H_NMR (success): {'result': '1H NMR (400 MHz, CDCl3): δ 7.65 (s, 4H), 4.28 – 4.17 (m, 2H), 4.04 (...]
node_5 --> node_6
node_7[Tool: Get_13C_NMR (success): {'result': '13C NMR (101 MHz, CDCl3): δ 133.06, 120.74, 88.13, 88.08, 82.61, 82....]
node_6 --> node_7
node_8[AI: Call Get_IR]
node_7 --> node_8
node_9[Tool: Get_IR (error): {'error': 'Sample 971ed2d0-d638-4d90-b4ad-f71ac4cd247d has no 'ir' data.'}]
node_8 --> node_9
node_10[AI: Call Get_HRMS]
node_9 --> node_10
node_11[Tool: Get_HRMS (success): {'result': 'HRMS (ESI+): m/z calc’d for C20H30NO6S2 (M+NH4)+: 444.1509, found: 4...]
node_10 --> node_11
node_12[AI: Call Calculate_DBE]
node_11 --> node_12
node_13[Tool: Calculate_DBE (success): {'result': 8.0}]
node_12 --> node_13
node_14[AI: {'type': 'text', 'text': 'Based on the spectroscopic data provided, the unknown ...]
node_13 --> node_14
node_15[AI: {'type': 'text', 'text': 'Based on the spectroscopic data provided, the unknown ...]
node_14 --> node_15
```