```mermaid
graph TD
node_0[User: 你是一名资深有机合成与波谱解析专家，正在一个虚拟实验室中 分析编号为 0ec455bd-c002-45f8-afb5-dd2373ffe896 的未知有机小分子...]
node_1[AI: Call Measure_Formula, Measure_MW, Calculate_DBE, Check_Data]
node_0 --> node_1
node_2[Tool: Measure_Formula (success): {'result': 'C20H29NO3'}]
node_1 --> node_2
node_3[Tool: Measure_MW (success): {'result': 331.214743788}]
node_2 --> node_3
node_4[Tool: Calculate_DBE (success): {'result': 7.0}]
node_3 --> node_4
node_5[Tool: Check_Data (success): {'result': ('Measure_MW', 'Measure_Formula', 'Get_1H_NMR', 'Get_13C_NMR', 'Get_I...]
node_4 --> node_5
node_6[AI: Call Get_1H_NMR, Get_13C_NMR, Get_IR]
node_5 --> node_6
node_7[Tool: Get_1H_NMR (success): {'result': '1H NMR (500 MHz, CDCl3) δ 7.74 (d, J = 8.6 Hz, 2H), 6.92 (d, J = 8.5...]
node_6 --> node_7
node_8[Tool: Get_13C_NMR (success): {'result': '13C NMR (126 MHz, CDCl3) δ 209.77, 167.12, 162.21, 128.75, 127.09, 1...]
node_7 --> node_8
node_9[Tool: Get_IR (success): {'result': 'IR (neat): 3326, 2941, 2864, 1712, 1632, 1606, 1545, 1504, 1458, 135...]
node_8 --> node_9
node_10[AI: {'type': 'text', 'text': '根据对所提供实验数据的详细解析，该化合物的结构推导如下：\n\n1. **分子式与不饱和度**：\n * 分...]
node_9 --> node_10
node_11[AI: {'type': 'text', 'text': '根据对谱学数据的综合解析，该化合物的结构推导如下：\n\n1. **分子式与不饱和度**：分子式为 $C_{...]
node_10 --> node_11
```