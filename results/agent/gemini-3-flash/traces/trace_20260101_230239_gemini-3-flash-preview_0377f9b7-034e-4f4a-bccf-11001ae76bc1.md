```mermaid
graph TD
node_0[User: 你是一名资深有机合成与波谱解析专家，正在一个虚拟实验室中 分析编号为 0377f9b7-034e-4f4a-bccf-11001ae76bc1 的未知有机小分子...]
node_1[AI: Call Check_Data]
node_0 --> node_1
node_2[Tool: Check_Data (success): {'result': ('Measure_MW', 'Measure_Formula', 'Get_1H_NMR', 'Get_13C_NMR', 'Get_I...]
node_1 --> node_2
node_3[AI: Call Measure_Formula, Measure_MW, Calculate_DBE]
node_2 --> node_3
node_4[Tool: Measure_Formula (success): {'result': 'C17H21NO2'}]
node_3 --> node_4
node_5[Tool: Measure_MW (success): {'result': 271.157228912}]
node_4 --> node_5
node_6[Tool: Calculate_DBE (success): {'result': 8.0}]
node_5 --> node_6
node_7[AI: Call Get_1H_NMR, Get_13C_NMR, Get_IR]
node_6 --> node_7
node_8[Tool: Get_1H_NMR (success): {'result': '1H NMR (500 MHz, CDCl3) δ 7.86 – 7.81 (m, 2H), 7.73 – 7.67 (m, 2H), ...]
node_7 --> node_8
node_9[Tool: Get_13C_NMR (success): {'result': '13C NMR (126 MHz, CDCl3) δ 168.62, 133.96, 132.32, 123.28, 38.51, 37...]
node_8 --> node_9
node_10[Tool: Get_IR (success): {'result': 'IR (neat): 2922, 2849, 1773, 1710, 1615, 1466, 1438, 1395, 1362, 118...]
node_9 --> node_10
node_11[AI: {'type': 'text', 'text': '根据波谱分析和分子式信息，该化合物的结构解析如下：\n\n1. **分子式与不饱和度**：分子式为 $C_{...]
node_10 --> node_11
node_12[AI: {'type': 'text', 'text': '根据波谱分析和分子式信息，该化合物的结构解析如下：\n\n1. **分子式与不饱和度**：分子式为 $C_{...]
node_11 --> node_12
```