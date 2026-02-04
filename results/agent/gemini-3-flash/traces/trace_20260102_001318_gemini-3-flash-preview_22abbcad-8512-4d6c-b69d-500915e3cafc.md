```mermaid
graph TD
node_0[User: 你是一名资深有机合成与波谱解析专家，正在一个虚拟实验室中 分析编号为 22abbcad-8512-4d6c-b69d-500915e3cafc 的未知有机小分子...]
node_1[AI: Call Measure_Formula, Measure_MW, Calculate_DBE]
node_0 --> node_1
node_2[Tool: Measure_Formula (success): {'result': 'C9H9N'}]
node_1 --> node_2
node_3[Tool: Measure_MW (success): {'result': 131.073499288}]
node_2 --> node_3
node_4[Tool: Calculate_DBE (success): {'result': 6.0}]
node_3 --> node_4
node_5[AI: Call Get_1H_NMR, Get_13C_NMR]
node_4 --> node_5
node_6[Tool: Get_1H_NMR (success): {'result': '1H NMR (500 MHz, CDCl3) δ 10.06 (s, 1 H), 8.18 (s, 1 H), 7.84-7.82 (...]
node_5 --> node_6
node_7[Tool: Get_13C_NMR (success): {'result': '13C NMR (125 MHz, CDCl3) δ 139.96, 130.73, 129.32, 128.23, 126.47, 1...]
node_6 --> node_7
node_8[AI: Call Get_IR]
node_7 --> node_8
node_9[Tool: Get_IR (error): {'error': 'Sample 22abbcad-8512-4d6c-b69d-500915e3cafc has no 'ir' data.'}]
node_8 --> node_9
node_10[AI: Call Check_Data]
node_9 --> node_10
node_11[Tool: Check_Data (success): {'result': ('Measure_MW', 'Measure_Formula', 'Get_1H_NMR', 'Get_13C_NMR')}]
node_10 --> node_11
node_12[AI: {'type': 'text', 'text': 'To identify the structure of the unknown organic molec...]
node_11 --> node_12
node_13[AI: {'type': 'text', 'text': '基于对该样品的波谱数据分析，推导过程如下：\n\n1. **分子式与不饱和度**：\n 分子式确定为 **C...]
node_12 --> node_13
```