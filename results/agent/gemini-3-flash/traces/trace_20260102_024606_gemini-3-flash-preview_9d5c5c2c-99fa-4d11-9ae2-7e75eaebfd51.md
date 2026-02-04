```mermaid
graph TD
node_0[User: 你是一名资深有机合成与波谱解析专家，正在一个虚拟实验室中 分析编号为 9d5c5c2c-99fa-4d11-9ae2-7e75eaebfd51 的未知有机小分子...]
node_1[AI: Call Measure_MW, Measure_Formula, Calculate_DBE]
node_0 --> node_1
node_2[Tool: Measure_MW (success): {'result': 270.102095718}]
node_1 --> node_2
node_3[Tool: Measure_Formula (success): {'result': 'C13H19O4P'}]
node_2 --> node_3
node_4[Tool: Calculate_DBE (success): {'result': 4.5}]
node_3 --> node_4
node_5[AI: Call Get_1H_NMR, Get_13C_NMR, Get_31P_NMR, Get_IR]
node_4 --> node_5
node_6[Tool: Get_1H_NMR (success): {'result': '1H NMR (600 MHz, CDCl3) δ 7.81 – 7.68 (m, 2H), 7.39 – 7.30 (m, 2H), ...]
node_5 --> node_6
node_7[Tool: Get_13C_NMR (success): {'result': '13C NMR (101 MHz, CDCl3) δ 185.07, 150.76, 132.79, 126.99, 68.15, 52...]
node_6 --> node_7
node_8[Tool: Get_31P_NMR (success): {'result': '31P NMR (243 MHz, CDCl3) δ 22.01'}]
node_7 --> node_8
node_9[Tool: Get_IR (error): {'error': 'Sample 9d5c5c2c-99fa-4d11-9ae2-7e75eaebfd51 has no 'ir' data.'}]
node_8 --> node_9
node_10[AI: Call Check_Data, Get_HRMS]
node_9 --> node_10
node_11[Tool: Check_Data (success): {'result': ('Measure_MW', 'Measure_Formula', 'Get_1H_NMR', 'Get_13C_NMR', 'Get_3...]
node_10 --> node_11
node_12[Tool: Get_HRMS (success): {'result': 'HRMS (ESI) m/z: M+H+ calculated for C12H20O4P+: 271.1094, found 271....]
node_11 --> node_12
node_13[AI: {'type': 'text', 'text': '针对该样品的解析过程如下：\n\n1. **分子式与不饱和度分析**：\n * 通过 `Measure_Fo...]
node_12 --> node_13
node_14[AI: {'type': 'text', 'text': '根据对谱学数据的详细解析，该化合物的分子式为 $C_{13}H_{19}O_4P$。其 $^1$H NMR ...]
node_13 --> node_14
```