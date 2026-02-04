```mermaid
graph TD
node_0[User: 你是一名资深有机合成与波谱解析专家，正在一个虚拟实验室中 分析编号为 5b3b0b2b-0d4d-42e7-b865-dd14ed2d4efd 的未知有机小分子...]
node_1[AI: Call Check_Data]
node_0 --> node_1
node_2[Tool: Check_Data (success): {'result': ('Measure_MW', 'Measure_Formula', 'Get_1H_NMR', 'Get_13C_NMR', 'Get_H...]
node_1 --> node_2
node_3[AI: Call Measure_Formula, Measure_MW]
node_2 --> node_3
node_4[Tool: Measure_Formula (success): {'result': 'C7H7Br'}]
node_3 --> node_4
node_5[Tool: Measure_MW (success): {'result': 169.973112324}]
node_4 --> node_5
node_6[AI: Call Get_1H_NMR, Get_13C_NMR]
node_5 --> node_6
node_7[Tool: Get_1H_NMR (success): {'result': 'δ H (400 MHz, Chloroform-d) 7.47 – 7.29 (5 H, m), 4.54 (2 H, s).'}]
node_6 --> node_7
node_8[Tool: Get_13C_NMR (success): {'result': 'δ C (101 MHz, Chloroform-d) 137.8, 129.1, 128.8, 128.5, 33.6.'}]
node_7 --> node_8
node_9[AI: {'type': 'text', 'text': '根据谱学数据分析如下：\n\n1. **分子式分析**：\n * 通过 `Measure_Formula` ...]
node_8 --> node_9
```