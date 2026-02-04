```mermaid
graph TD
node_0[User: 你是一名资深有机合成与波谱解析专家，正在一个虚拟实验室中 分析编号为 e2c7048e-ead7-43dd-ac65-f9353d3bff83 的未知有机小分子...]
node_1[AI: Call Check_Data]
node_0 --> node_1
node_2[Tool: Check_Data (success): {'result': ('Measure_MW', 'Measure_Formula', 'Get_1H_NMR', 'Get_13C_NMR', 'Get_I...]
node_1 --> node_2
node_3[AI: Call Measure_MW, Measure_Formula]
node_2 --> node_3
node_4[Tool: Measure_MW (success): {'result': 364.215078136}]
node_3 --> node_4
node_5[Tool: Measure_Formula (success): {'result': 'C23H28N2O2'}]
node_4 --> node_5
node_6[AI: Call Get_1H_NMR, Get_13C_NMR]
node_5 --> node_6
node_7[Tool: Get_1H_NMR (success): {'result': '1H NMR (500 MHz, CDCl3) δ = 7.79 (d, J = 7.5 Hz, 2H), 7.39-7.36 (m, ...]
node_6 --> node_7
node_8[Tool: Get_13C_NMR (success): {'result': '13C NMR (126 MHz, CDCl3) δ = 167.19, 162.09, 137.63, 129.28, 128.84,...]
node_7 --> node_8
node_9[AI: ]
node_8 --> node_9
node_10[AI: 基于综合分析，该未知有机小分子最可能的结构如下： **自然语言分析：** 1. **分子信息**：分子式C₂₃H₂₈N₂O₂（MW=364.21），DBE=11...]
node_9 --> node_10
```