```mermaid
graph TD
node_0[User: 你是一名资深有机合成与波谱解析专家，正在一个虚拟实验室中 分析编号为 de28aa89-b7fe-4c2b-8e96-6da52b9761a8 的未知有机小分子...]
node_1[AI: Call Check_Data]
node_0 --> node_1
node_2[Tool: Check_Data (success): {'result': ('Measure_MW', 'Measure_Formula', 'Get_1H_NMR', 'Get_13C_NMR', 'Get_I...]
node_1 --> node_2
node_3[AI: Call Measure_MW, Measure_Formula]
node_2 --> node_3
node_4[Tool: Measure_MW (success): {'result': 320.121258004}]
node_3 --> node_4
node_5[Tool: Measure_Formula (success): {'result': 'C21H17FO2'}]
node_4 --> node_5
node_6[AI: Call Get_1H_NMR, Get_13C_NMR]
node_5 --> node_6
node_7[Tool: Get_1H_NMR (success): {'result': '1H NMR (300 MHz, CDCl3) δ 2.40 (br s, 6H), 7.15-7.34 (m, 10H). Carbo...]
node_6 --> node_7
node_8[Tool: Get_13C_NMR (success): {'result': '13C NMR (75 MHz, CDCl3, C-F coupling constants assigned where possib...]
node_7 --> node_8
node_9[AI: Call Get_IR]
node_8 --> node_9
node_10[Tool: Get_IR (success): {'result': 'FT-IR (neat, cm-1) υ 1701, 1469, 1287.'}]
node_9 --> node_10
node_11[AI: {'type': 'text', 'text': '通过对提供的数据进行系统分析，得出以下结论：\n\n1. **分子式与不饱和度**：\n * 分子式为 $C...]
node_10 --> node_11
node_12[AI: {'type': 'text', 'text': '根据对提供的波谱数据和分子信息的系统分析，该未知化合物的结构解析如下：\n\n1. **分子式与不饱和度**...]
node_11 --> node_12
```