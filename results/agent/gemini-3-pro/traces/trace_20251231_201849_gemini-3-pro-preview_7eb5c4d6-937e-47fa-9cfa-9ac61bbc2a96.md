```mermaid
graph TD
node_0[User: 你是一名资深有机合成与波谱解析专家，正在一个虚拟实验室中 分析编号为 7eb5c4d6-937e-47fa-9cfa-9ac61bbc2a96 的未知有机小分子...]
node_1[AI: Call Check_Data, Measure_Formula, Measure_MW]
node_0 --> node_1
node_2[Tool: Check_Data (success): {'result': ('Measure_MW', 'Measure_Formula', 'Get_1H_NMR', 'Get_13C_NMR', 'Get_I...]
node_1 --> node_2
node_3[Tool: Measure_Formula (success): {'result': 'C21H31NO6'}]
node_2 --> node_3
node_4[Tool: Measure_MW (success): {'result': 393.21513771199994}]
node_3 --> node_4
node_5[AI: Call Get_1H_NMR, Get_13C_NMR, Get_IR]
node_4 --> node_5
node_6[Tool: Get_1H_NMR (success): {'result': '1H NMR (500 MHz, CDCl3) δ = 7.75 (d, J = 7.5 Hz, 2H), 6.89 (d, J = 7...]
node_5 --> node_6
node_7[Tool: Get_13C_NMR (success): {'result': '13C NMR (126 MHz, CDCl3) δ = 170.55, 169.89, 167.04, 162.00, 128.68,...]
node_6 --> node_7
node_8[Tool: Get_IR (success): {'result': 'IR (neat): 3322, 2953, 1732, 1632, 1606, 1503, 1435, 1252, 1178, 114...]
node_7 --> node_8
node_9[AI: Call Get_HRMS]
node_8 --> node_9
node_10[Tool: Get_HRMS (success): {'result': 'HRMS (ESI) exact mass calculated for (M+Na)+ (C21H31NaNO6) requires ...]
node_9 --> node_10
node_11[AI: {'type': 'text', 'text': '基于已有的详细波谱数据，可以对该分子进行完整的结构解析。\n\n### 1. 分子式与基础信息\n- **分...]
node_10 --> node_11
```