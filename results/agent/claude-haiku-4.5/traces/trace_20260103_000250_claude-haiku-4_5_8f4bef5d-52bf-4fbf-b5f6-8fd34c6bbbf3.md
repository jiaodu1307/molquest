```mermaid
graph TD
node_0[User: 你是一名资深有机合成与波谱解析专家，正在一个虚拟实验室中 分析编号为 8f4bef5d-52bf-4fbf-b5f6-8fd34c6bbbf3 的未知有机小分子...]
node_1[AI: Call Check_Data, Measure_MW, Measure_Formula]
node_0 --> node_1
node_2[Tool: Check_Data (success): {'result': ('Measure_MW', 'Measure_Formula', 'Get_1H_NMR', 'Get_13C_NMR', 'Get_M...]
node_1 --> node_2
node_3[Tool: Measure_MW (success): {'result': 283.229999928}]
node_2 --> node_3
node_4[Tool: Measure_Formula (success): {'result': 'C20H29N'}]
node_3 --> node_4
node_5[AI: Call Calculate_DBE, Get_1H_NMR, Get_13C_NMR, Get_MS]
node_4 --> node_5
node_6[Tool: Calculate_DBE (success): {'result': 7.0}]
node_5 --> node_6
node_7[Tool: Get_1H_NMR (success): {'result': '1H NMR (300 MHz, CD2Cl2): δ = 7.60 (s_br, 1H), 7.34-7.26 (m, 2H), 7....]
node_6 --> node_7
node_8[Tool: Get_13C_NMR (success): {'result': '13C NMR (75 MHz, CD2Cl2): δ = 140.9, 132.8, 129.5, 129.1, 129.0, 126...]
node_7 --> node_8
node_9[Tool: Get_MS (success): {'result': 'MS (70 eV, EI); m/z (%): 283 (21, M+), 184 (8), 170 (100), 156 (3), ...]
node_8 --> node_9
node_10[AI: Call Get_IR]
node_9 --> node_10
node_11[Tool: Get_IR (error): {'error': 'Sample 8f4bef5d-52bf-4fbf-b5f6-8fd34c6bbbf3 has no 'ir' data.'}]
node_10 --> node_11
node_12[AI: ## 最终结构推断 基于所有可用数据，我推断该化合物为 **N-苯甲基-十一烯胺** 或类似的长链烯胺。 关键证据： 1. **分子式 C₂₀H₂₉N**，DB...]
node_11 --> node_12
node_13[AI: 基于前面的详细分析，我给出最终结论： ## 结构解析总结 根据获取的谱学数据： **分子式**：C₂₀H₂₉N **分子量**：283.23 Da **不饱和度...]
node_12 --> node_13
```