```mermaid
graph TD
node_0[User: 你是一名资深有机合成与波谱解析专家，正在一个虚拟实验室中 分析编号为 9120f8a8-03dc-4efa-b283-bf201cff8247 的未知有机小分子...]
node_1[AI: Call Measure_Formula, Measure_MW, Calculate_DBE]
node_0 --> node_1
node_2[Tool: Measure_Formula (success): {'result': 'C12H16O'}]
node_1 --> node_2
node_3[Tool: Measure_MW (success): {'result': 176.120115132}]
node_2 --> node_3
node_4[Tool: Calculate_DBE (success): {'result': 5.0}]
node_3 --> node_4
node_5[AI: Call Get_1H_NMR, Get_13C_NMR, Get_IR]
node_4 --> node_5
node_6[Tool: Get_1H_NMR (success): {'result': '1H NMR (400 MHz, CDCl3) δ 7.14 (s, 4H), 4.10 – 4.06 (m, 2H), 3.53 (t...]
node_5 --> node_6
node_7[Tool: Get_13C_NMR (error): {'error': 'Sample 9120f8a8-03dc-4efa-b283-bf201cff8247 has no '13c_nmr' data.'}]
node_6 --> node_7
node_8[Tool: Get_IR (error): {'error': 'Sample 9120f8a8-03dc-4efa-b283-bf201cff8247 has no 'ir' data.'}]
node_7 --> node_8
node_9[AI: Call Check_Data]
node_8 --> node_9
node_10[Tool: Check_Data (success): {'result': ('Measure_MW', 'Measure_Formula', 'Get_1H_NMR')}]
node_9 --> node_10
node_11[AI: {'type': 'text', 'text': '基于对该样品的波谱数据分析，以下是解析过程：\n\n1. **分子式与不饱和度**：\n * 通过 `Mea...]
node_10 --> node_11
node_12[AI: {'type': 'text', 'text': '根据对该样品的波谱数据分析，解析过程如下：\n\n1. **分子式与不饱和度**：\n * 分子式为 **C...]
node_11 --> node_12
```