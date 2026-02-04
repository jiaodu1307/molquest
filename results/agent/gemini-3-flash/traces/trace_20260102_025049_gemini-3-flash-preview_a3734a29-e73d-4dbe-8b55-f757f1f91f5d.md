```mermaid
graph TD
node_0[User: 你是一名资深有机合成与波谱解析专家，正在一个虚拟实验室中 分析编号为 a3734a29-e73d-4dbe-8b55-f757f1f91f5d 的未知有机小分子...]
node_1[AI: Call Check_Data]
node_0 --> node_1
node_2[Tool: Check_Data (success): {'result': ('Measure_MW', 'Measure_Formula', 'Get_1H_NMR', 'Get_13C_NMR', 'Get_I...]
node_1 --> node_2
node_3[AI: Call Measure_MW, Measure_Formula]
node_2 --> node_3
node_4[Tool: Measure_MW (success): {'result': 361.26169398}]
node_3 --> node_4
node_5[Tool: Measure_Formula (success): {'result': 'C22H35NO3'}]
node_4 --> node_5
node_6[AI: Call Calculate_DBE, Get_IR, Get_1H_NMR, Get_13C_NMR]
node_5 --> node_6
node_7[Tool: Calculate_DBE (success): {'result': 6.0}]
node_6 --> node_7
node_8[Tool: Get_IR (success): {'result': 'IR (neat): 3328, 2949, 1713, 1632, 1607, 1545, 1504, 1464, 1362, 129...]
node_7 --> node_8
node_9[Tool: Get_1H_NMR (success): {'result': '1H NMR (500 MHz, CDCl3) δ 7.73 (d, J = 8.4 Hz, 2H), 6.92 (d, J = 8.6...]
node_8 --> node_9
node_10[Tool: Get_13C_NMR (success): {'result': '13C NMR (126 MHz, CDCl3) δ 209.67, 167.14, 162.22, 128.75, 127.06, 1...]
node_9 --> node_10
node_11[AI: {'type': 'text', 'text': '根据对该样品的理化性质和波谱数据的详细解析，推断如下：\n\n1. **分子式与不饱和度**：\n 通过 `...]
node_10 --> node_11
node_12[AI: {'type': 'text', 'text': '根据对该样品的理化性质和波谱数据的详细解析，推断如下：\n\n1. **分子式与不饱和度**：\n 通过 `...]
node_11 --> node_12
```