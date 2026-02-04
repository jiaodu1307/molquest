```mermaid
graph TD
node_0[User: 你是一名资深有机合成与波谱解析专家，正在一个虚拟实验室中 分析编号为 7fff51dd-9012-46e3-88e1-48cce1dbff9c 的未知有机小分子...]
node_1[AI: Call Measure_MW, Measure_Formula, Check_Data]
node_0 --> node_1
node_2[Tool: Measure_MW (success): {'result': 403.18172940799997}]
node_1 --> node_2
node_3[Tool: Measure_Formula (success): {'result': 'C22H29NO4S'}]
node_2 --> node_3
node_4[Tool: Check_Data (success): {'result': ('Measure_MW', 'Measure_Formula', 'Get_1H_NMR', 'Get_13C_NMR', 'Get_I...]
node_3 --> node_4
node_5[AI: Call Get_1H_NMR, Get_13C_NMR, Get_IR, Get_HRMS]
node_4 --> node_5
node_6[Tool: Get_1H_NMR (success): {'result': '1H NMR (500 MHz, CDCl3) δ 7.88 – 7.83 (m, 2H), 7.57 (t, J = 7.4 Hz, ...]
node_5 --> node_6
node_7[Tool: Get_13C_NMR (success): {'result': '13C NMR (126 MHz, CDCl3) δ 175.35, 140.76, 140.09, 132.71, 129.23, 1...]
node_6 --> node_7
node_8[Tool: Get_IR (success): {'result': 'IR (neat): 3284, 2953, 2870, 1731, 1471, 1446, 1434, 1367, 1325, 120...]
node_7 --> node_8
node_9[Tool: Get_HRMS (success): {'result': 'HRMS (ESI) exact mass calculated for (M+H)+ (C22H30NO4S) requires m/...]
node_8 --> node_9
node_10[AI: 基于完整的谱学数据分析，我推断该化合物的结构如下： **结构特征总结：** 1. **两个苯环**：一个单取代苯环（5H）和一个对位二取代苯环（4H）- 占 8...]
node_9 --> node_10
node_11[AI: FINAL_RESULT: UUID: 7fff51dd-9012-46e3-88e1-48cce1dbff9c PREDICTED_SMILES: Cc1cc...]
node_10 --> node_11
```