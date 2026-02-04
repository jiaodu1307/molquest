```mermaid
graph TD
node_0[User: 你是一名资深有机合成与波谱解析专家，正在一个虚拟实验室中 分析编号为 cdc34d12-da9d-4fa6-bad0-48ab473bb291 的未知有机小分子...]
node_1[AI: Call Measure_Formula, Measure_MW, Check_Data]
node_0 --> node_1
node_2[Tool: Measure_Formula (success): {'result': 'C11H14O'}]
node_1 --> node_2
node_3[Tool: Measure_MW (success): {'result': 162.104465068}]
node_2 --> node_3
node_4[Tool: Check_Data (success): {'result': ('Measure_MW', 'Measure_Formula', 'Get_1H_NMR')}]
node_3 --> node_4
node_5[AI: Call Get_1H_NMR]
node_4 --> node_5
node_6[Tool: Get_1H_NMR (success): {'result': '1H NMR (400 MHz, CDCl3) δ7.31 – 7.35 (m, 2H), 7.24 – 7.20 (m, 3H), 4...]
node_5 --> node_6
node_7[AI: Call Get_13C_NMR, Get_IR]
node_6 --> node_7
node_8[Tool: Get_13C_NMR (error): {'error': 'Sample cdc34d12-da9d-4fa6-bad0-48ab473bb291 has no '13c_nmr' data.'}]
node_7 --> node_8
node_9[Tool: Get_IR (error): {'error': 'Sample cdc34d12-da9d-4fa6-bad0-48ab473bb291 has no 'ir' data.'}]
node_8 --> node_9
node_10[AI: {'type': 'text', 'text': '根据对编号为 `cdc34d12-da9d-4fa6-bad0-48ab473bb291` 的样品的波谱分析...]
node_9 --> node_10
node_11[AI: {'type': 'text', 'text': '根据对该样品的波谱数据分析，其分子式为 C₁₁H₁₄O，不饱和度为 5。¹H NMR 谱图显示在 δ 7.2...]
node_10 --> node_11
```