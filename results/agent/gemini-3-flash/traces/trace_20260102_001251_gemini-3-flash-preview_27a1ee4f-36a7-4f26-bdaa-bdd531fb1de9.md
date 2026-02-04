```mermaid
graph TD
node_0[User: 你是一名资深有机合成与波谱解析专家，正在一个虚拟实验室中 分析编号为 27a1ee4f-36a7-4f26-bdaa-bdd531fb1de9 的未知有机小分子...]
node_1[AI: Call Measure_Formula, Check_Data]
node_0 --> node_1
node_2[Tool: Measure_Formula (success): {'result': 'C6H9Br'}]
node_1 --> node_2
node_3[Tool: Check_Data (success): {'result': ('Measure_MW', 'Measure_Formula', 'Get_1H_NMR', 'Get_13C_NMR')}]
node_2 --> node_3
node_4[AI: Call Get_1H_NMR, Get_13C_NMR]
node_3 --> node_4
node_5[Tool: Get_1H_NMR (success): {'result': 'δ H (500 MHz, Chloroform-d) 5.97 – 5.90 (1 H, m), 5.88 – 5.73 (1 H, ...]
node_4 --> node_5
node_6[Tool: Get_13C_NMR (success): {'result': 'δ C (126 MHz, Chloroform-d) 131.1, 128.9, 49.1, 32.7, 24.7, 18.5'}]
node_5 --> node_6
node_7[AI: {'type': 'text', 'text': '通过对编号为 27a1ee4f-36a7-4f26-bdaa-bdd531fb1de9 的样品进行波谱分析，...]
node_6 --> node_7
node_8[AI: {'type': 'text', 'text': '通过对波谱数据的详细解析，该化合物的分子式为 $C_6H_9Br$，不饱和度（DBE）为 2。13C NMR...]
node_7 --> node_8
```