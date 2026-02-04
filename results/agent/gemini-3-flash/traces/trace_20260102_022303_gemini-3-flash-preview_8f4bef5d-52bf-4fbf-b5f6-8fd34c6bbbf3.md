```mermaid
graph TD
node_0[User: 你是一名资深有机合成与波谱解析专家，正在一个虚拟实验室中 分析编号为 8f4bef5d-52bf-4fbf-b5f6-8fd34c6bbbf3 的未知有机小分子...]
node_1[AI: Call Check_Data]
node_0 --> node_1
node_2[Tool: Check_Data (success): {'result': ('Measure_MW', 'Measure_Formula', 'Get_1H_NMR', 'Get_13C_NMR', 'Get_M...]
node_1 --> node_2
node_3[AI: Call Measure_MW, Measure_Formula]
node_2 --> node_3
node_4[Tool: Measure_MW (success): {'result': 283.229999928}]
node_3 --> node_4
node_5[Tool: Measure_Formula (success): {'result': 'C20H29N'}]
node_4 --> node_5
node_6[AI: Call Get_1H_NMR, Get_13C_NMR]
node_5 --> node_6
node_7[Tool: Get_1H_NMR (success): {'result': '1H NMR (300 MHz, CD2Cl2): δ = 7.60 (s_br, 1H), 7.34-7.26 (m, 2H), 7....]
node_6 --> node_7
node_8[Tool: Get_13C_NMR (success): {'result': '13C NMR (75 MHz, CD2Cl2): δ = 140.9, 132.8, 129.5, 129.1, 129.0, 126...]
node_7 --> node_8
node_9[AI: {'type': 'text', 'text': '根据对提供的数据分析，该样品的分子式为 $C_{20}H_{29}N$，不饱和度为 7。\n\n**1. 核...]
node_8 --> node_9
node_10[AI: {'type': 'text', 'text': '根据提供的数据分析，该样品的分子式为 $C_{20}H_{29}N$，不饱和度（DBE）为 7。\n\n**...]
node_9 --> node_10
```