```mermaid
graph TD
node_0[User: 你是一名资深有机合成与波谱解析专家，正在一个虚拟实验室中 分析编号为 7eb5c4d6-937e-47fa-9cfa-9ac61bbc2a96 的未知有机小分子...]
node_1[AI: Call Measure_MW, Measure_Formula]
node_0 --> node_1
node_2[Tool: Measure_MW (success): {'result': 393.21513771199994}]
node_1 --> node_2
node_3[Tool: Measure_Formula (success): {'result': 'C21H31NO6'}]
node_2 --> node_3
node_4[AI: Call Check_Data]
node_3 --> node_4
node_5[Tool: Check_Data (success): {'result': ('Measure_MW', 'Measure_Formula', 'Get_1H_NMR', 'Get_13C_NMR', 'Get_I...]
node_4 --> node_5
node_6[AI: Call Get_1H_NMR, Get_13C_NMR, Get_IR, Get_HRMS]
node_5 --> node_6
node_7[Tool: Get_1H_NMR (success): {'result': '1H NMR (500 MHz, CDCl3) δ = 7.75 (d, J = 7.5 Hz, 2H), 6.89 (d, J = 7...]
node_6 --> node_7
node_8[Tool: Get_13C_NMR (success): {'result': '13C NMR (126 MHz, CDCl3) δ = 170.55, 169.89, 167.04, 162.00, 128.68,...]
node_7 --> node_8
node_9[Tool: Get_IR (success): {'result': 'IR (neat): 3322, 2953, 1732, 1632, 1606, 1503, 1435, 1252, 1178, 114...]
node_8 --> node_9
node_10[Tool: Get_HRMS (success): {'result': 'HRMS (ESI) exact mass calculated for (M+Na)+ (C21H31NaNO6) requires ...]
node_9 --> node_10
node_11[AI: 让我继续分析这个复杂的结构。从数据来看，这似乎是一个天然产物或药物分子的衍生物。让我尝试构建更精确的结构模型。 **关键观察**： 1. 对位取代苯环（AA'B...]
node_10 --> node_11
node_12[AI: FINAL_RESULT: UUID: 7eb5c4d6-937e-47fa-9cfa-9ac61bbc2a96 PREDICTED_SMILES: COC(=...]
node_11 --> node_12
```