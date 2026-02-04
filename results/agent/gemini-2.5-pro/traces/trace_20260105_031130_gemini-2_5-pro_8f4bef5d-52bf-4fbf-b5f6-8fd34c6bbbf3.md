```mermaid
graph TD
node_0[User: 你是一名资深有机合成与波谱解析专家，正在一个虚拟实验室中 分析编号为 8f4bef5d-52bf-4fbf-b5f6-8fd34c6bbbf3 的未知有机小分子...]
node_1[AI: Call Measure_Formula]
node_0 --> node_1
node_2[Tool: Measure_Formula (success): {'result': 'C20H29N'}]
node_1 --> node_2
node_3[AI: Call Measure_MW, Get_1H_NMR, Get_13C_NMR]
node_2 --> node_3
node_4[Tool: Measure_MW (success): {'result': 283.229999928}]
node_3 --> node_4
node_5[Tool: Get_1H_NMR (success): {'result': '1H NMR (300 MHz, CD2Cl2): δ = 7.60 (s_br, 1H), 7.34-7.26 (m, 2H), 7....]
node_4 --> node_5
node_6[Tool: Get_13C_NMR (success): {'result': '13C NMR (75 MHz, CD2Cl2): δ = 140.9, 132.8, 129.5, 129.1, 129.0, 126...]
node_5 --> node_6
node_7[AI: {'type': 'text', 'text': '好的，我已经获取了初始数据，现在开始解析。\n\n第一步：分析基本信息\n- 分子式：C20H29N\n- ...]
node_6 --> node_7
node_8[AI: FINAL_RESULT: UUID: 8f4bef5d-52bf-4fbf-b5f6-8fd34c6bbbf3 PREDICTED_SMILES: CCCCC...]
node_7 --> node_8
```