```mermaid
graph TD
node_0[User: 你是一名资深有机合成与波谱解析专家，正在一个虚拟实验室中 分析编号为 a863e2fc-ddae-4d15-b6c4-a530c7f4aa5d 的未知有机小分子...]
node_1[AI: Call Check_Data, Measure_Formula]
node_0 --> node_1
node_2[Tool: Check_Data (success): {'result': ('Measure_MW', 'Measure_Formula', 'Get_1H_NMR', 'Get_13C_NMR')}]
node_1 --> node_2
node_3[Tool: Measure_Formula (success): {'result': 'C14H12'}]
node_2 --> node_3
node_4[AI: Call Get_1H_NMR, Get_13C_NMR]
node_3 --> node_4
node_5[Tool: Get_1H_NMR (success): {'result': '1H NMR (500 MHz, CDCl3) δ 7.56-7.54 (d, J = 7.5 Hz, 4 H), 7.41-7.38 ...]
node_4 --> node_5
node_6[Tool: Get_13C_NMR (success): {'result': '13C NMR (125 MHz, CDCl3) δ 137.35, 128.71, 128.70, 127.64, 126.53'}]
node_5 --> node_6
node_7[AI: {'type': 'text', 'text': '通过对样品 **a863e2fc-ddae-4d15-b6c4-a530c7f4aa5d** 的分析，我已确...]
node_6 --> node_7
```