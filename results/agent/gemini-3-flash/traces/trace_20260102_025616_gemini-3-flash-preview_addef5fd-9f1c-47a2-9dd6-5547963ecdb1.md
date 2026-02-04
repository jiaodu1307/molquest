```mermaid
graph TD
node_0[User: 你是一名资深有机合成与波谱解析专家，正在一个虚拟实验室中 分析编号为 addef5fd-9f1c-47a2-9dd6-5547963ecdb1 的未知有机小分子...]
node_1[AI: Call Check_Data]
node_0 --> node_1
node_2[Tool: Check_Data (success): {'result': ('Measure_MW', 'Measure_Formula', 'Get_1H_NMR', 'Get_13C_NMR', 'Get_H...]
node_1 --> node_2
node_3[AI: Call Measure_Formula, Measure_MW]
node_2 --> node_3
node_4[Tool: Measure_Formula (success): {'result': 'C14H20O4'}]
node_3 --> node_4
node_5[Tool: Measure_MW (success): {'result': 252.13615912}]
node_4 --> node_5
node_6[AI: Call Get_1H_NMR, Get_13C_NMR]
node_5 --> node_6
node_7[Tool: Get_1H_NMR (success): {'result': '1H NMR (400 MHz, CDCl3) δ 6.44 (s, 2H), 4.11 – 4.05 (m, 2H), 3.86 (s...]
node_6 --> node_7
node_8[Tool: Get_13C_NMR (success): {'result': '13C NMR (151 MHz, CDCl3) δ 153.20, 141.74, 136.40, 103.65, 68.34, 60...]
node_7 --> node_8
node_9[AI: Call Get_HRMS]
node_8 --> node_9
node_10[Tool: Get_HRMS (success): {'result': 'HRMS (ESI) m/z: M+H+ calculated for C14H21O4+: 253.1434, found 253.1...]
node_9 --> node_10
node_11[AI: {'type': 'text', 'text': '基于对样品 addef5fd-9f1c-47a2-9dd6-5547963ecdb1 的波谱数据分析，解析过...]
node_10 --> node_11
node_12[AI: {'type': 'text', 'text': '根据提供的波谱数据，该未知小分子的结构解析如下：\n\n1. **分子式与不饱和度**：通过 `Measur...]
node_11 --> node_12
```