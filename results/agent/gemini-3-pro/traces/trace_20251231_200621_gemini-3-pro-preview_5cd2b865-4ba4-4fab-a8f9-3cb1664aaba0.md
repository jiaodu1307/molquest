```mermaid
graph TD
node_0[User: 你是一名资深有机合成与波谱解析专家，正在一个虚拟实验室中 分析编号为 5cd2b865-4ba4-4fab-a8f9-3cb1664aaba0 的未知有机小分子...]
node_1[AI: Call Check_Data]
node_0 --> node_1
node_2[Tool: Check_Data (success): {'result': ('Measure_MW', 'Measure_Formula', 'Get_1H_NMR', 'Get_13C_NMR', 'Get_H...]
node_1 --> node_2
node_3[AI: Call Measure_Formula, Measure_MW]
node_2 --> node_3
node_4[Tool: Measure_Formula (success): {'result': 'C12H16Cl2O2'}]
node_3 --> node_4
node_5[Tool: Measure_MW (success): {'result': 262.052735112}]
node_4 --> node_5
node_6[AI: Call Get_1H_NMR, Get_13C_NMR]
node_5 --> node_6
node_7[Tool: Get_1H_NMR (success): {'result': '1H NMR (400 MHz, CDCl3) δ 7.36 (d, J = 8.2 Hz, 1H), 7.27 – 7.25 (m, ...]
node_6 --> node_7
node_8[Tool: Get_13C_NMR (success): {'result': '13C NMR (101 MHz, CDCl3) δ 144.91, 132.39, 130.38, 130.07, 129.53, 1...]
node_7 --> node_8
node_9[AI: Call Get_IR]
node_8 --> node_9
node_10[Tool: Get_IR (error): {'error': 'Sample 5cd2b865-4ba4-4fab-a8f9-3cb1664aaba0 has no 'ir' data.'}]
node_9 --> node_10
node_11[AI: Call Calculate_DBE]
node_10 --> node_11
node_12[Tool: Calculate_DBE (success): {'result': 4.0}]
node_11 --> node_12
node_13[AI: {'type': 'text', 'text': '通过一系列谱学数据的分析，我们可以确定该未知分子的结构。\n\n1. **分子式与不饱和度**：\n * 通...]
node_12 --> node_13
```